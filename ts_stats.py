import sys
import os
import argparse
import json
import pathlib
import SimpleITK as sitk
import pandas as pd
import numpy as np
from totalsegmentator.statistics import get_radiomics_features
from totalsegmentator.map_to_binary import class_map
import tempfile

def split_path_into_subdirectories(path):
  """Splits a path into a list of its subdirectories."""
  all_parts = []
  while True:
    parts = os.path.split(path)
    if parts[0] == path:  # For absolute paths
      all_parts.insert(0, parts[0])
      break
    elif parts[1] == path:  # For relative paths
      all_parts.insert(0, parts[1])
      break
    else:
      path = parts[0]
      all_parts.insert(0, parts[1])
  return all_parts

#/cbica/projects/pmbb-vision/subjects/A123/4567/PMBBIDA1234567XXX/Accession/StudyUID/PMBBID_Accession_Date_SeriesNum_SeriesName/PMBBID_Accession_Date_SeriesNum_SeriesName_ext.nii.gz
def parse_image_filename(img_name):

    fname = os.path.abspath(img_name)
    #img_dirname = os.path.dirname(fname)
    #img_basename = os.path.basename(fname)

    parts = split_path_into_subdirectories(fname)
    dat={}
    dat["pmbbid"] = parts[7]
    dat["accession_number"] = parts[8]
    dat["study_uid"] = parts[9]
    series_info = parts[10]
    dat["series_number"] = series_info.split('_')[3]
    dat["series_name"] = series_info.split('_')[4]

    return(dat)

def get_data_row():
    row = {}
    row['id'] = 'NA'
    row['accession_number'] = 'NA'
    row['series_number'] = 'NA'
    row['series_name'] = 'NA'
    row['label_system'] = 'NA'
    row['label_name'] = 'NA'
    row['label_number'] = 'NA'
    row['calculator'] = 'NA'
    row['measure'] = 'NA'
    row['metric'] = 'NA'
    row['value'] = 'NA'
    return(row)

#unused
def value_list_to_string( val, seperator='|' ):
    
    if isinstance(val, list):
        val_str = [ str(x) for x in val ]
        ret_str = seperator.join(val_str)
    elif isinstance(val, dict):
        ret_str=""
        for k in val.keys():
            ret_str = ret_str + str(val[k])
    else:
        ret_str = str(val)

    return(ret_str)

def get_json_stats(json_file):

    dat=[]
    f = open(json_file, 'r')
    jdat = json.load(f)
    f.close()

    if 'Image' in jdat:
        for k in jdat['Image']:
            image_entry = jdat['Image'][k]
            if isinstance(image_entry, list):
                for (idx,ivalue) in enumerate(image_entry):
                    row = get_data_row()
                    row['label_system']='nifti'
                    row['label_name']='header' 
                    row['label_number']='NA'
                    row['calculator']='itk'
                    row['measure']=k
                    row['metric']=str(idx)
                    row['value']=str(ivalue)
                    dat.append(row)
            else:
                row = get_data_row()
                row['label_system']='nifti'
                row['label_name']='header'
                row['label_number']='NA'
                row['calculator']='itk'
                row['measure']=k
                row['metric']='NA'
                row['value']=str(image_entry)
                dat.append(row)            

    if 'Dicom' in jdat:
        for k in jdat['Dicom']:
            if k != 'InstanceList':
                tag_entry = jdat['Dicom'][k]
                if tag_entry['vr']=='SQ':
                    sq = tag_entry['Value']
                    for sq_entry in sq:
                        for sub_k in sq_entry.keys():
                            sub_entry = sq_entry[sub_k]
                            for (idx, ivalue) in enumerate(sub_entry['Value']):
                                row = get_data_row()
                                row['label_system']='dicom'
                                row['label_name']=tag_entry['Group']
                                row['label_number']=tag_entry['Element']
                                row['calculator']='dicom'
                                row['measure']=k+'_'+sub_k
                                row['metric']=str(idx)
                                row['value']=str(ivalue).replace(",", "/")
                                dat.append(row)
                else:
                    if tag_entry['Value'] is not None:
                        for (idx, ivalue) in enumerate(tag_entry['Value']):
                            row = get_data_row()
                            row['label_system']='dicom'
                            row['label_name']=tag_entry['Group']
                            row['label_number']=tag_entry['Element']
                            row['calculator']='dicom'
                            row['measure']=k
                            row['metric']=str(idx)
                            row['value']=str(ivalue).replace(",", "/")
                            dat.append(row)
    return(dat)

def mask_on_border(img):
    arr = sitk.GetArrayViewFromImage(img)
    if np.sum(arr[0,:,:]) > 0:
        return True
    if np.sum(arr[:,0,:]) > 0:
        return True
    if np.sum(arr[:,:,0]) > 0:
        return True    
    if np.sum(arr[arr.shape[0]-1,:,:]) > 0:
        return True
    if np.sum(arr[:,arr.shape[1]-1,:]) > 0:
        return True
    if np.sum(arr[:,:,arr.shape[2]-1]) > 0:
        return True   
    return False

def get_radiomics_stats(img_name, seg_name, names, values):

    seg = sitk.ReadImage(seg_name)
    odir = os.path.dirname(os.path.abspath(seg_name))
    obase = os.path.basename(seg_name).split('.')[0]

    tbase=None
    if 'LSB_JOB_TMPDIR' in os.environ:
        tbase = os.environ["LSB_JOB_TMPDIR"]
    else:
        tbase = "/tmp"
    tdir = tempfile.TemporaryDirectory(dir=tbase, prefix=obase)

    dat={}
    for name, value in zip(names, values):

        iname = os.path.join(tdir.name, obase+'_'+str(name)+'.nii.gz')
        imask = seg==value

        if len(np.unique(sitk.GetArrayViewFromImage(imask))) > 1:
            sitk.WriteImage(imask, iname)
            #print("Rad stats for "+name)
            (label_name, istats) = get_radiomics_features(pathlib.Path(iname),pathlib.Path(img_name))
            on_border = mask_on_border(imask)
            istats['shape_OnBorder']=int(on_border)
            os.remove(iname)
            dat[name]=istats
        
    tdir.cleanup()

    return(dat)

def get_shape_stats(img, mask, names, values):

    stats = sitk.LabelIntensityStatisticsImageFilter()
    stats.SetBackgroundValue(0)
    stats.ComputeFeretDiameterOn()
    stats.ComputePerimeterOn()
    #stats.ComputeOrientedBoundingBoxOff() # v2.4.0

    dat={}

    try:
        stats.Execute( mask, img )

        index=0
        for name, value in zip(names, values):
            ival=int(value)
            #imask = mask==ival
            #on_border = mask_on_border(imask)

            if stats.HasLabel(value):
                dict={}
                dict["firstorder_Mean"] = stats.GetMean(ival)
                dict["firstorder_Minimum"] = stats.GetMinimum(ival)
                dict["firstorder_Maximum"] = stats.GetMaximum(ival)
                dict["firstorder_Median"] = stats.GetMedian(ival)
                dict["firstorder_StandardDeviation"] = stats.GetStandardDeviation(ival)
                dict["firstorder_Skewness"] = stats.GetSkewness(ival)

                dict["shape_Volume"] = stats.GetPhysicalSize(ival)
                dict["shape_GetNumberOfPixelsOnBorder"] = stats.GetNumberOfPixelsOnBorder(ival)
                dict["shape_NumberOfPixels"] = stats.GetNumberOfPixels(ival)
                dict["shape_Roundness"] = stats.GetRoundness(ival)
                dict["shape_Elongation"] = stats.GetElongation(ival)
                dict["shape_Flatness"] = stats.GetFlatness(ival)
                dict["shape_WeightedElongation"] = stats.GetWeightedElongation(ival)
                dict["shape_WeightedFlatness"] = stats.GetWeightedFlatness(ival)
                dict["shape_Kurtosis"] = stats.GetKurtosis(ival)
                dict["shape_EquivalentEllipsoidDiameter0"] = stats.GetEquivalentEllipsoidDiameter(ival)[0]
                dict["shape_EquivalentEllipsoidDiameter1"] = stats.GetEquivalentEllipsoidDiameter(ival)[1]
                dict["shape_EquivalentEllipsoidDiameter2"] = stats.GetEquivalentEllipsoidDiameter(ival)[2]
                dict["shape_EquivalentSphericalRadius"] = stats.GetEquivalentSphericalRadius(ival)
                dict["shape_EquivalentSphericalPerimeter"] = stats.GetEquivalentSphericalPerimeter(ival)

                dict["shape_FeretDiameter"] = stats.GetFeretDiameter(ival)
                
                dict["shape_GetNumberOfPixelsOnBorder"] = stats.GetNumberOfPixelsOnBorder(ival)
                dict["shape_PerimeterOnBorder"] = stats.GetPerimeterOnBorder(ival)
                dict["shape_PerimeterOnBorderRatio"] = stats.GetPerimeterOnBorderRatio(ival)
                dict["shape_Perimeter"] = stats.GetPerimeter(ival)



                dat[name]=dict

            index+=1
    except RuntimeError as e:
        print("Exception occured in JabbaReport.get_shape_stats(): " + str(e))
        return None

    return dat

def main():

    my_parser = argparse.ArgumentParser(description='Summarize processed directory')
    my_parser.add_argument('-i', '--input', type=str, help='input ct image', required=True)
    my_parser.add_argument('-o', '--output', type=str, help='output csv', required=True)
    my_parser.add_argument('-s', '--seg', type=str, help='merged seg', required=True)
    my_parser.add_argument('-m', '--meta', action='store_true', default=False, required=False)
    args = my_parser.parse_args()



    if not os.path.exists(args.seg):
        print("Input does not exist: "+args.seg)
        return(1)
    if not os.path.exists(args.input):
        print("Input does not exist: "+args.input)
        return(1)        


    # Merge labels from part1 and part2
    # Higher index takes priority (this is how TS does it)
    seg = sitk.ReadImage(args.seg)
    img = sitk.ReadImage(args.input)

    img_basename = os.path.basename(args.input)
    img_basename = img_basename.split(".")[0]
    img_dirname = os.path.dirname(os.path.abspath(args.input))

    img_info = parse_image_filename(args.input)

    #json_name = os.path.join(img_dirname, img_basename+'.json')
    #json_stats=[]
    #if args.meta:
    #    json_stats = get_json_stats(json_name)

    #print("get_radiomics_stats")
    rad_stats = get_radiomics_stats(args.input, args.seg, class_map['total'].values(),class_map['total'].keys())

    #print("get_simpleitk_stats")
    sitk_stats = get_shape_stats(img,seg,class_map['total'].values(),class_map['total'].keys())
    row_dat = []

    name_parts = img_basename.split("_")
    calid = name_parts[0]
    acc = name_parts[1]
    series_num = name_parts[2]
    series_name = '_'.join(name_parts[3:len(name_parts)])

    #for n in json_stats:
    #    n['id'] = calid
    #    n['accession_number'] = acc
    #    n['series_number'] = series_num
    #    n['series_name'] = series_name
    #    row_dat.append(n)

    mydict = class_map['total']
    for idx in class_map['total'].keys():
        n = class_map['total'][idx]
        if n in rad_stats:
            for stat in rad_stats[n].keys():
                row = get_data_row()
                row['pmbbid'] = img_info['pmbbid']
                row['accession_number'] = img_info['accession_number']
                row['study_uid'] = img_info['study_uid']
                row['series_number'] = img_info['series_number']
                row['series_name'] = img_info['series_name']
                row['label_name'] = n
                row['label_number'] = idx
                row['label_system'] = 'totalsegmentator'
                row['calculator'] = 'pyradiomics'
                row['measure'] = stat.split('_')[0]
                row['metric'] = stat.split('_')[1]
                row['value'] = str(rad_stats[n][stat])
                #print( n + " " + stat + " " + str(rad_stats[n][stat]) )
                row_dat.append(row)
        if n in sitk_stats:
            for stat in sitk_stats[n].keys():
                row = get_data_row()
                row['pmbbid'] = img_info['pmbbid']
                row['accession_number'] = img_info['accession_number']
                row['study_uid'] = img_info['study_uid']
                row['series_number'] = img_info['series_number']
                row['series_name'] = img_info['series_name']
                row['label_name'] = n
                row['label_number'] = idx
                row['label_system'] = 'totalsegmentator'
                row['calculator'] = "simpleitk"
                row['measure'] = stat.split('_')[0]
                row['metric'] = stat.split('_')[1]
                row['value'] = str(sitk_stats[n][stat])
                #print( n + " " + stat + " " + str(sitk_stats[n][stat]))
                row_dat.append(row)
    
    df = pd.DataFrame.from_dict(row_dat)

    if df.size > 0:
        df.to_csv(args.output, index=False, na_rep='NA')


if __name__=="__main__":
    main()
