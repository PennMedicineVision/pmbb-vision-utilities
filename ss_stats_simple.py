import sys
import os
import argparse
import json
import time
import pathlib
import SimpleITK as sitk
import pandas as pd
import numpy as np

import tempfile
import radiomics

def synthseg_labels():
    names = ["left cerebral white matter",
             "left cerebral cortex",
             "left lateral ventricle",
             "left inferior lateral ventricle",
             "left cerebellum white matter",
             "left cerebellum cortex",
             "left thalamus",
             "left caudate",
             "left putamen",
             "left pallidum",
             "3rd ventricle",
             "4th ventricle",
             "brain-stem",
             "left hippocampus",
             "left amygdala",
             "left accumbens area",
             "CSF","left ventral DC",
             "right cerebral white matter",
             "right cerebral cortex",
             "right lateral ventricle",
             "right inferior lateral ventricle",
             "right cerebellum white matter",
             "right cerebellum cortex",
             "right thalamus",
             "right caudate",
             "right putamen",
             "right pallidum",
             "right hippocampus",
             "right amygdala",
             "right accumbens area",
             "right ventral DC",
             "left bankssts",
             "left caudalanteriorcingulate",
             "left caudalmiddlefrontal",
             "left corpuscallosum ",
             "left cuneus",
             "left entorhinal",
             "left fusiform",
             "left inferiorparietal",
             "left inferiortemporal",
             "left isthmuscingulate",
             "left lateraloccipital",
             "left lateralorbitofrontal",
             "left lingual",
             "left medialorbitofrontal",
             "left middletemporal",
             "left parahippocampal",
             "left paracentral",
             "left parsopercularis",
             "left parsorbitalis",
             "left parstriangularis",
             "left pericalcarine",
             "left postcentral",
             "left posteriorcingulate",
             "left precentral",
             "left precuneus",
             "left rostralanteriorcingulate",
             "left rostralmiddlefrontal",
             "left superiorfrontal",
             "left superiorparietal",
             "left superiortemporal",
             "left supramarginal",
             "left frontalpole",
             "left temporalpole",
             "left transversetemporal",
             "left insula",
             "right unknown",
             "right bankssts",
             "right caudalanteriorcingulate",
             "right caudalmiddlefrontal",
             "right corpuscallosum",
             "right cuneus",
             "right entorhinal",
             "right fusiform",
             "right inferiorparietal",
             "right inferiortemporal",
             "right isthmuscingulate",
             "right lateraloccipital",
             "right lateralorbitofrontal",
             "right lingual",
             "right medialorbitofrontal",
             "right middletemporal",
             "right parahippocampal",
             "right paracentral",
             "right parsopercularis",
             "right parsorbitalis",
             "right parstriangularis",
             "right pericalcarine",
             "right postcentral",
             "right posteriorcingulate",
             "right precentral",
             "right precuneus",
             "right rostralanteriorcingulate",
             "right rostralmiddlefrontal",
             "right superiorfrontal",
             "right superiorparietal",
             "right superiortemporal",
             "right supramarginal",
             "right frontalpole",
             "right temporalpole",
             "right transversetemporal",
             "right insula"]
    values = [0,2,3,4,5,7,8,10,11,12,13,14,15,16,17,18,26,
              24,28,41,42,43,44,46,47,49,50,51,52,53,54,58,60,
              1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,
              1011,1012,1013,1014,1015,1016,1017,1018,1019,1020,
              1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,
              1031,1032,1033,1034,1035,2000,2001,2002,2003,2004,
              2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,
              2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,
              2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035]

    return( (names, values) )

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

# /cbica/projects/pmbb-vision/processing/synthseg/A100/9169/PMBBA1009169679/31575492/2.25.160417019112203539104154602063221533907/PMBBA1009169679_31575492_20240813000000_11001_AXIAL_DTI_30_DIRECTIONS_BRAIN_TRACEW/PMBBA1009169679_31575492_20240813000000_11001_AXIAL_DTI_30_DIRECTIONS_BRAIN_TRACEW_resampled.nii.gz
def parse_image_filename(img_name):

    fname = os.path.abspath(img_name)
    parts = split_path_into_subdirectories(fname)

    dat={}
    dat["pmbb_vision_id"] = parts[8]
    dat["accession_number"] = parts[9]
    dat["study_uid"] = parts[10]
    series_info = parts[11]
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

    (names, values) = synthseg_labels()

    print("get_radiomics_stats")
    t1 = time.perf_counter()
    rad_stats = get_radiomics_stats(img,seg,values,names)
    t2 = time.perf_counter()
    rad_time=t2-t1
    print(f"radiomics run time: {rad_time} seconds")

    print("get_simpleitk_stats")
    t3 = time.perf_counter()
    sitk_stats = get_shape_stats(img,seg,values,names)
    t4 = time.perf_counter()    
    itk_time=t4-t3
    print(f"SimpleITK run time: {itk_time} seconds")

    row_dat = []
    row_dat_eff = []

    for idx, label in enumerate(values):
        nm = names[idx]
        if nm in rad_stats:
            for stat in rad_stats[n].keys():
                row = get_data_row()
                row['id'] = img_info['pmbb_vision_id']
                row['accession_number'] = img_info['accession_number']
                row['study_uid'] = img_info['study_uid']
                row['series_number'] = img_info['series_number']
                row['series_name'] = img_info['series_name']
                row['image_filename'] = os.path.basename(args.input)
                row['labels_filename'] = os.path.basename(args.seg)
                row['label_name'] = nm
                row['label_number'] = label
                row['label_system'] = 'synthseg'
                row['calculator'] = 'pyradiomics'
                row['measure'] = stat.split('_')[0]
                row['metric'] = stat.split('_')[1]
                row['value'] = str(rad_stats[nm][stat])
                row_dat.append(row)
        if nm in sitk_stats:
            for stat in sitk_stats[n].keys():
                row = get_data_row()
                row['id'] = img_info['pmbb_vision_id']
                row['accession_number'] = img_info['accession_number']
                row['study_uid'] = img_info['study_uid']
                row['series_number'] = img_info['series_number']
                row['series_name'] = img_info['series_name']
                row['image_filename'] = os.path.basename(args.input)
                row['labels_filename'] = os.path.basename(args.seg)
                row['label_name'] = nm
                row['label_number'] = label
                row['label_system'] = 'synthseg'
                row['calculator'] = "simpleitk"
                row['measure'] = stat.split('_')[0]
                row['metric'] = stat.split('_')[1]
                row['value'] = str(sitk_stats[nm][stat])

                row_dat.append(row)


    df = pd.DataFrame.from_dict(row_dat)
    df_eff = pd.DataFrame.from_dict(row_dat_eff)

    if df.size > 0:
        df.to_csv(args.output[0], index=False, na_rep='NA')

    if df_eff.size > 0:
        df_eff.to_csv(args.output[1], index=False, na_rep='NA')


if __name__=="__main__":
    main()
