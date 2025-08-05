#!/bin/bash

dir="$1"
tdir="$2"
index="$3"

offset=$SLURM_ARRAY_TASK_ID


echo "Index file = $index"
cat="cat $index"
if [ "$index" == "*.parquet" ]; then
  cat="parquet-tools csv $index"
fi

max_offset=$($cat | wc | xargs | cut -d " " -f1)
if (( offset > max_offset )); then
    echo "TaskID exceeds array size" 1>&2
    echo "TaskID = $SLURM_ARRAY_TASK_ID"
    echo "offset = $offset"
    echo "max task id = $max_offset"
    exit 2
fi

sub_line=$($cat | head -n $offset | tail -n 1)

# get subdirectory to summarize
subdir=$(echo $sub_line | xargs)
subdir_name=`basename $subdir`

id_file="${tdir}/${subdir_name}_pmbbvid.txt"
report_file="${tdir}/${subdir_name}_reports.txt"
study_file="${tdir}/${subdir_name}_studies.csv"
echo "Writing ID list to: $id_file"

# Get list of all PMBBIDs that have a dicom directory
find ${subdir} -maxdepth 2 -name PMBB* -type d -exec sh -c 'echo $(basename {})' \; >> ${id_file}

# Get list of all dicom directories that have at least 1 report
find ${subdir} -maxdepth 4 -name Diag* -type d >> ${report_file}

# Get a list of all studies in dicom directory
# Add line index for easier use in slurm array jobs
find ${subdir} -maxdepth 3 -mindepth 3 -type d -exec sh -c 'echo "$(echo {} | xargs dirname | xargs basename),$(basename {})"' \; >> $study_file
#cat ${s1_file} | { sed -u q; nl -s ',' -n rn; } > $s2_file
#rm ${s1_file}


#if [ "$getsubs" -eq 1 ]; then 
#  find /cbica/projects/pmbb-vision/subjects -maxdepth 4 -mindepth 4 -type d -exec sh -c 'echo "$(echo {} | xargs dirname | xargs basename),$(basename {})"' \; > /cbica/projects/pmbb-vision/info/pmbbid_subject_accessions.csv

#  find /cbica/projects/pmbb-vision/subjects -maxdepth 5 -mindepth 5 -type d -exec sh -c 'echo "$(echo {} | xargs dirname | xargs basename),$(basename {})"' \; > /cbica/projects/pmbb-vision/info/pmbbid_subject_studies.csv

#  find /cbica/projects/pmbb-vision/subjects -maxdepth 3 -name PMBB* -type d -exec sh -c 'echo $(basename {})' \; > /cbica/projects/pmbb-vision/info/pmbbid_subjects.txt

 # find /cbica/projects/pmbb-vision/subjects -name *.nii.gz -type f > /cbica/projects/pmbb-vision/info/pmbbid_nifti_volumes.txt

#  find /cbica/projects/pmbb-vision/subjects -name *report000.json -type f > /cbica/projects/pmbb-vision/info/pmbbid_subject_reports.txt
#fi


