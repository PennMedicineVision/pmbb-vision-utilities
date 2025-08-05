#!/bin/bash

dir=""
output=""

while getopts "d:o:" option; do
   case $option in
      d) dir=$OPTARG;;
      o) output=$OPTARG;;
   esac
done

dir=`realpath $dir`
output=`realpath $output`
name=`basename $dir`
odir=`dirname $output`

#echo $dir
#echo $name
#echo $odir

# Does input directory exist
if [ ! -d "$dir" ]; then
  echo "Directory not found: $dir"
  exit 1
fi

# Create output directory if necessary
if [ ! -d "$odir" ]; then
  mkdir -o $odir
fi

temp_dir=$(mktemp -d -p ${odir})
echo "Created $temp_dir"

echo "Creating directory index.."
ls -d ${dir}/[A-Z]* > ${temp_dir}/index.txt
echo "  Done"

N=`cat ${temp_dir}/index.txt | wc | xargs | cut -d " " -f1 | xargs`

cmd="sbatch --parsable --array=1-$N --time=0:10:0 --partition=all --mem=10 --output=${temp_dir}/log.out --error=${temp_dir}/log.err  dicom_summary_slurm.sh $dir $temp_dir ${temp_dir}/index.txt"
echo "$cmd"
array_job=`$cmd`;

finish_1=`sbatch --parsable --dependency=afterany:${array_job} --output=${output}_log.out --error=${output}_log.err  --time=1:00:0 --partition=all --mem=10 dicom_summary_slurm_finish.sh $temp_dir $output`

studies="${output}_studies.csv"
cmd2="sbatch --parsable --dependency=afterany:${finish_1} --array=1-$N --time=3:0:0 --partition=all --mem=10 --output=${temp_dir}/log2.out --error=${temp_dir}/log2.err dicom_details_slurm.sh $dir $temp_dir ${temp_dir}/index.txt $studies"
echo "$cmd2"
array_job_2=`$cmd2`;

finish_2=`sbatch --parsable --dependency=afterany:${array_job_2} --output=${output}_details_log.out --error=${output}_details_log.err  --time=1:00:0 --partition=all --mem=10 dicom_details_slurm_finish.sh $temp_dir $output`

echo "Quick Array Job: $array_job"
echo "Quick Array Finisher: $finish_1"
echo "Slow Array Job: $array_job_2"
echo "Slow Array Finisher: $finish_2"




