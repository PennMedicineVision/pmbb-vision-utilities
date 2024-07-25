#!/bin/bash
module load slurm/current

usage() { echo "Usage: $0 -i input_list.txt"; exit 1; } 

DICOMTREEPATH="/cbica/projects/pmbb-vision/pkg/dicom_tree"

dicombase="/cbica/projects/pmbb-vision/dicom"
reconbase="/cbica/projects/pmbb-vision/subjects"
inputfile=""
subject=""

while getopts d:hi:s:r: flag
do 
  case "${flag}" in
     i) inputfile=${OPTARG};;
     d) dicombase=${OPTARG};;
     r) reconbase=${OPTARG};;
     s) subject=${OPTARG};;
     h) usage;;
  esac
done

while read id; do
  d1=${id:4:4}
  d2=${id:8:4}
  subdir="${dicombase}/${d1}/${d2}/${id}"
  outdir="${reconbase}/${d1}/${d2}/${id}"

  # get all studies for the subject
  studies=$(ls $subdir)
  for st in $studies; do 
    
    sout="${outdir}/${st}"

    # Ignore studies with existing output
    if [ ! -e "${sout}" ]; then 

      echo $id

      job_dir="${sout}/slurm"
      if [ ! -e "$job_dir" ]; then
        mkdir -p $job_dir
      fi

      drdir="${subdir}/${st}/Diagnostic Report"
      if [ -e "$drdir" ]; then
        files=$(ls "$drdir")
        fn=0
        for f in $files; do
          acc=`dcmdump "${drdir}/$f" | grep AccessionNumber | cut -d '[' -f2 | cut -d ']' -f1 | xargs`
          json_name=$(printf "${sout}/Diagnostic-Report/${id}_${acc}_report%03d.json" "$fn")

          job=$(printf "${job_dir}/${id}_${acc}_report%03d.sh" "$fn")
          job_out=$(printf "${job_dir}/${id}_${acc}_report%03d.out" "$fn")
          job_err=$(printf "${job_dir}/${id}_${acc}_report%03d.err" "$fn")
          echo "#!/bin/bash" > $job
          echo "#SBATCH --output=${job_out}" >>  $job
          echo "#SBATCH --error=${job_err}" >> $job
          echo "mkdir -p ${sout}/Diagnostic-Report" >> $job
          echo "dcm2json \"${drdir}/$f\" $json_name" >> $job
          echo "rmdir ${sout}/Diagnostic-Report 2> /dev/null" >> $job
          sbatch $job

          fn=$((fn+1))
        done
      fi

      # get all numbered series directories
      series=$(ls -d ${subdir}/${st}/[0-9]*)
      for se in $series; do

        # Create script for this series
        sename=$(basename $se)
        job="${job_dir}/${id}_${st}_${sename}.sh"
        echo "#!/bin/bash" > $job
        echo "#SBATCH --output=${job_dir}/${id}_${st}_${sename}.out" >>  $job
        echo "#SBATCH --error=${job_dir}/${id}_${st}_${sename}.err" >> $job
        echo "${DICOMTREEPATH}/scripts/dcm2niix_wrap.sh -i $se -o ${outdir}/${st}/${sename} -n ${id}_%g" >> $job
        echo "rmdir ${outdir}/${st}/${sename} 2> /dev/null" >> $job

        # submit the job to run
        echo $job
        sbatch $job
      done
    fi


  done
done < $inputfile

