import sys
import os
import argparse
import json
import time
import pathlib
import SimpleITK as sitk
import pandas as pd
import numpy as np
from totalsegmentator.statistics import get_radiomics_features
from totalsegmentator.map_to_binary import class_map
import tempfile
import radiomics

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
    parts = split_path_into_subdirectories(fname)

    dat={}
    dat["pmbb_vision_id"] = parts[7]
    dat["accession_number"] = parts[8]
    dat["study_uid"] = parts[9]
    series_info = parts[10]
    sparts=series_info.split('_')

    dat["series_number"] = sparts[3]
    dat["series_name"] = "_".join(sparts[4:len(sparts)])
    return(dat)

def get_data_row():
    row = {}
    row['id'] = 'NA'
    row['accession_number'] = 'NA'
    row['study_uid'] = 'NA'
    row['series_number'] = 'NA'
    row['series_name'] = 'NA'
    row['image_filename'] = 'NA'
    row['labels_filename'] = 'NA'
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

def get_radiomics_stats(img, seg, names, values):

    dict={}
    for name, value in zip(names, values):

        #print(str(value) + " " + name)
        imask = seg==value

        if len(np.unique(sitk.GetArrayViewFromImage(imask))) > 1:
            stats1=radiomics.firstorder.RadiomicsFirstOrder(img,imask).execute()
            stats2=radiomics.shape.RadiomicsShape(img,imask).execute()
        idict={}
        for k in stats1.keys():
            idict['firstorder_'+k] = stats1[k]
        for k in stats2.keys():
            idict['shape_'+k] = stats2[k]
        dict[name]=idict

    return(dict)

def get_firstorder_stats(img, mask, names, values):

    stats = sitk.LabelIntensityStatisticsImageFilter()
    stats.SetBackgroundValue(0)
    stats.ComputeFeretDiameterOff()
    stats.ComputePerimeterOff()

    dat={}

    try:
        stats.Execute( mask, img )

        index=0
        for name, value in zip(names, values):
            ival=int(value)

            if stats.HasLabel(value):
                dict={}
                dict["firstorder_Mean"] = stats.GetMean(ival)
                dict["firstorder_Minimum"] = stats.GetMinimum(ival)
                dict["firstorder_Maximum"] = stats.GetMaximum(ival)
                dict["firstorder_Median"] = stats.GetMedian(ival)
                dict["firstorder_StandardDeviation"] = stats.GetStandardDeviation(ival)
                dict["firstorder_Skewness"] = stats.GetSkewness(ival)

                dict["shape_Volume"] = stats.GetPhysicalSize(ival)
                dict["shape_NumberOfPixels"] = stats.GetNumberOfPixels(ival)
                dict["shape_GetNumberOfPixelsOnBorder"] = stats.GetNumberOfPixelsOnBorder(ival)

                dat[name]=dict

            index+=1
    except RuntimeError as e:
        print("Exception occured in get_firstorder_stats(): " + str(e))
        return None

    return dat


def get_shape_stats(img, mask, names, values):

    stats = sitk.LabelIntensityStatisticsImageFilter()
    stats.SetBackgroundValue(0)
    stats.ComputeFeretDiameterOff()
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
                #print(name)
                dict={}
                dict["firstorder_Mean"] = stats.GetMean(ival)
                dict["firstorder_Minimum"] = stats.GetMinimum(ival)
                dict["firstorder_Maximum"] = stats.GetMaximum(ival)
                dict["firstorder_Median"] = stats.GetMedian(ival)
                dict["firstorder_StandardDeviation"] = stats.GetStandardDeviation(ival)
                dict["firstorder_Skewness"] = stats.GetSkewness(ival)

                dict["shape_Volume"] = stats.GetPhysicalSize(ival)
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
                #dict["shape_FeretDiameter"] = stats.GetFeretDiameter(ival)
                
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
    my_parser.add_argument('-o', '--output', type=str, help='output csv', nargs='+', required=True)
    my_parser.add_argument('-s', '--seg', type=str, help='merged seg', required=True)
    my_parser.add_argument('-e', '--effusion', type=str, help='effusion labels', required=False)
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
    print(img_info)

    #json_name = os.path.join(img_dirname, img_basename+'.json')
    #json_stats=[]
    #if args.meta:
    #    json_stats = get_json_stats(json_name)

    print("get_radiomics_stats")
    t1 = time.perf_counter()
    #rad_stats = get_radiomics_stats(args.input, args.seg, class_map['total'].values(),class_map['total'].keys())
    rad_stats = get_radiomics_stats(img,seg,class_map['total'].values(),class_map['total'].keys())
    #rad_stats=[]
    t2 = time.perf_counter()
    rad_time=t2-t1
    print(f"radiomics run time: {rad_time} seconds")

    print("get_simpleitk_stats")
    t3 = time.perf_counter()
    sitk_stats = get_shape_stats(img,seg,class_map['total'].values(),class_map['total'].keys())
    t4 = time.perf_counter()    
    itk_time=t4-t3
    print(f"SimpleITK run time: {itk_time} seconds")

    row_dat = []
    row_dat_eff = []

    mydict = class_map['total']
    for idx in class_map['total'].keys():
        n = class_map['total'][idx]
        if n in rad_stats:
            for stat in rad_stats[n].keys():
                row = get_data_row()
                row['id'] = img_info['pmbb_vision_id']
                row['accession_number'] = img_info['accession_number']
                row['study_uid'] = img_info['study_uid']
                row['series_number'] = img_info['series_number']
                row['series_name'] = img_info['series_name']
                row['image_filename'] = os.path.basename(args.input)
                row['labels_filename'] = os.path.basename(args.seg)
                row['label_name'] = n
                row['label_number'] = idx
                row['label_system'] = 'totalsegmentator_total_ct'
                row['calculator'] = 'pyradiomics'
                row['measure'] = stat.split('_')[0]
                row['metric'] = stat.split('_')[1]
                row['value'] = str(rad_stats[n][stat])
                row_dat.append(row)
        if n in sitk_stats:
            for stat in sitk_stats[n].keys():
                row = get_data_row()
                row['id'] = img_info['pmbb_vision_id']
                row['accession_number'] = img_info['accession_number']
                row['study_uid'] = img_info['study_uid']
                row['series_number'] = img_info['series_number']
                row['series_name'] = img_info['series_name']
                row['image_filename'] = os.path.basename(args.input)
                row['labels_filename'] = os.path.basename(args.seg)
                row['label_name'] = n
                row['label_number'] = idx
                row['label_system'] = 'totalsegmentator_total_ct'
                row['calculator'] = "simpleitk"
                row['measure'] = stat.split('_')[0]
                row['metric'] = stat.split('_')[1]
                row['value'] = str(sitk_stats[n][stat])

                row_dat.append(row)
    
    if args.effusion:
        eff = sitk.ReadImage(args.effusion)
        eff_names = ['pleural_effusion', 'pericardial_effusion']
        eff_values = [2,3]
        eff_stats = get_firstorder_stats(img,eff,eff_names,eff_values)
        count=0

        for n in eff_names:
            idx=eff_values[count]
            count=count+1

            if n in eff_stats:
                for stat in eff_stats[n].keys():
                    row = get_data_row()
                    row['id'] = img_info['pmbb_vision_id']
                    row['accession_number'] = img_info['accession_number']
                    row['study_uid'] = img_info['study_uid']
                    row['series_number'] = img_info['series_number']
                    row['series_name'] = img_info['series_name']
                    row['image_filename'] = os.path.basename(args.input)
                    row['labels_filename'] = os.path.basename(args.seg)
                    row['label_name'] = n
                    row['label_number'] = idx
                    row['label_system'] = 'totalsegmentator_pleural_pericardial_effusion'
                    row['calculator'] = "simpleitk"
                    row['measure'] = stat.split('_')[0]
                    row['metric'] = stat.split('_')[1]
                    row['value'] = str(eff_stats[n][stat])

                    row_dat_eff.append(row)

    df = pd.DataFrame.from_dict(row_dat)
    df_eff = pd.DataFrame.from_dict(row_dat_eff)

    if df.size > 0:
        df.to_csv(args.output[0], index=False, na_rep='NA')

    if df_eff.size > 0:
        df_eff.to_csv(args.output[1], index=False, na_rep='NA')


if __name__=="__main__":
    main()
