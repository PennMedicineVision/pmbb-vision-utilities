#!/bin/bash

# create a list of all subjects with an unprocessed study
#  pipe the output to a file to be used as input for build_subjects.sh
# example call
# sh list_subs_new_studies.sh /cbica/projects/pmbb-vision/dicom /cbica/projects/pmbb-vision/subjects > /cbica/projects/pmbb-vision/scripts/subject_list_DATE.txt

input_base=$1
output_base=$2

allsubs=$(ls -d ${input_base}/*/*/*)
for s in $allsubs; do
  id=`basename $s`;
  d1=${id:4:4}
  d2=${id:8:4}
    
  studies=$(ls $s)
  for st in $studies; do
    uid=$(basename $st)

    dicomdir="${input_base}/${d1}/${d2}/${id}/${uid}"
    outdir="${output_base}/${d1}/${d2}/${id}/${uid}"

    if [ ! -e "$outdir" ]; then
      #ls -l  $dicomdir
      echo $id
    fi
  done

done




