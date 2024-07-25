# pmbb-vision-utilities
Scripts and tools for managing the pmbb-vision dataset

## Basic Info
Currently, data is being processed on the cubic cluster. Incoming dicom data is stored at /cbica/projects/pmbb-vision/dicom. Subdirectories for each subject are determined from the PMBB ID. These IDs are of the form PMBB followed by 1 letter and then 10 digits. The first subdirectory is the letter and the first 3 digits, and the second level of directories is the next 4 digits. Then the full PMBBID is used, followed by StudyUID and finally a directory of the form SeriesNumber-SeriesDescription. So for example, for a subject with the ID of PMBBIDA0123456789. The directory /cbica/projects/pmbb-vision/dicom/A012/3456/PMBBA0123456789 would contain a directory for each study for that subject. The same directory scheme is used for the nifti and json data stored in /cbica/projects/pmbb-vision/subjects. 

## How to
To generate a list of all subjects that have at least one study that has not been converted to nifti and json, run the following

``
sh list_subs_new_studies.sh /cbica/projects/pmbb-vision/dicom /cbica/projects/pmbb-vision/subjects > /cbica/projects/pmbb-vision/scripts/subject_list_DATE.txt
``

To create nifti and json files for new dicom studies, run

``
sh build_subjects.sh -i /cbica/projects/pmbb-vision/scripts/subject_list_DATE.txt -d /cbica/projects/pmbb-vision/dicom -r /cbica/projects/pmbb-vision/subjects
``

The above script will only process studies that do not already have a directory in /cbica/projects/pmbb-vision/subjects. To rerun a study, you will need to delete that studies directory in /cbica/projects/pmbb-vision/subjects or direct the output to a different location

