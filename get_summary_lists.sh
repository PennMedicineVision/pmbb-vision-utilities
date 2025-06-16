#!/bin/bash
#SBATCH --output=/cbica/projects/pmbb-vision/logs/get_summary_lists_%j.out
#SBATCH --error=/cbica/projects/pmbb-vision/logs/get_summary_lists_%j.err

datatype="$1"
getsubs="$2"

# Get list of all PMBBIDs that have a dicom directory
echo "PMBBID" > /cbica/projects/pmbb-vision/info/pmbbid_${datatype}.txt
find /cbica/projects/pmbb-vision/${datatype} -maxdepth 3 -name PMBB* -type d -exec sh -c 'echo $(basename {})' \; >> /cbica/projects/pmbb-vision/info/pmbbid_${datatype}.txt

# Get list of all dicom directories that have at least 1 report
echo "Directory" > /cbica/projects/pmbb-vision/info/pmbbid_${datatype}_reports.txt
find /cbica/projects/pmbb-vision/${datatype} -maxdepth 5 -name Diag* -type d >> /cbica/projects/pmbb-vision/info/pmbbid_${datatype}_reports.txt

# Get a list of all studies in dicom directory
# Add line index for easier use in slurm array jobs
echo "Index,PMBBID,StudyUID" > /cbica/projects/pmbb-vision/info/pmbbid_${datatype}_studies_temp.csv
find /cbica/projects/pmbb-vision/${datatype} -maxdepth 4 -mindepth 4 -type d -exec sh -c 'echo "$(echo {} | xargs dirname | xargs basename),$(basename {})"' \; >> /cbica/projects/pmbb-vision/info/pmbbid_${datatype}_studies_temp.csv
cat /cbica/projects/pmbb-vision/info/pmbbid_${datatype}_studies_temp.csv | { sed -u q; nl -s ',' -n rn; } > /cbica/projects/pmbb-vision/info/pmbbid_${datatype}_studies.csv
rm /cbica/projects/pmbb-vision/info/pmbbid_${datatype}_studies_temp.csv

if [ "$getsubs" -eq 1 ]; then 
  find /cbica/projects/pmbb-vision/subjects -maxdepth 4 -mindepth 4 -type d -exec sh -c 'echo "$(echo {} | xargs dirname | xargs basename),$(basename {})"' \; > /cbica/projects/pmbb-vision/info/pmbbid_subject_accessions.csv

  find /cbica/projects/pmbb-vision/subjects -maxdepth 5 -mindepth 5 -type d -exec sh -c 'echo "$(echo {} | xargs dirname | xargs basename),$(basename {})"' \; > /cbica/projects/pmbb-vision/info/pmbbid_subject_studies.csv

  find /cbica/projects/pmbb-vision/subjects -maxdepth 3 -name PMBB* -type d -exec sh -c 'echo $(basename {})' \; > /cbica/projects/pmbb-vision/info/pmbbid_subjects.txt

  find /cbica/projects/pmbb-vision/subjects -name *.nii.gz -type f > /cbica/projects/pmbb-vision/info/pmbbid_nifti_volumes.txt

  find /cbica/projects/pmbb-vision/subjects -name *report000.json -type f > /cbica/projects/pmbb-vision/info/pmbbid_subject_reports.txt
fi


