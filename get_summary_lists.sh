#!/bin/bash


find /cbica/projects/pmbb-vision/subjects -maxdepth 3 -name PMBB* -type d -exec sh -c 'echo $(basename {})' \; > /cbica/projects/pmbb-vision/info/pmbbid_subjects.txt
find /cbica/projects/pmbb-vision/dicom -maxdepth 5 -name Diag* -type d > /cbica/projects/pmbb-vision/info/pmbbid_dicom_reports.txt
find /cbica/projects/pmbb-vision/dicom -maxdepth 3 -name PMBB* -type d -exec sh -c 'echo $(basename {})' \; > /cbica/projects/pmbb-vision/info/pmbbid_dicom.txt
find /cbica/projects/pmbb-vision/subjects -maxdepth 4 -mindepth 4 -type d -exec sh -c 'echo "$(echo {} | xargs dirname | xargs basename),$(basename {})"' \; > /cbica/projects/pmbb-vision/info/pmbbid_subject_studies.csv
find /cbica/projects/pmbb-vision/dicom -maxdepth 4 -mindepth 4 -type d -exec sh -c 'echo "$(echo {} | xargs dirname | xargs basename),$(basename {})"' \; > /cbica/projects/pmbb-vision/info/pmbbid_dicom_studies.csv
find /cbica/projects/pmbb-vision/subjects -name *.nii.gz -type f > /cbica/projects/pmbb-vision/info/pmbbid_nifti_volumes.txt
find /cbica/projects/pmbb-vision/subjects -name *report000.json -type f > /cbica/projects/pmbb-vision/info/pmbbid_subject_reports.txt


