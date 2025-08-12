#!/bin/bash

function is_abdomen() {
  in_name="$1"
  aliases=("ABDOMEN"
    "ABDOMEN_CT_ABD_UNEN_PE"
    "ABDOMEN_PELVIS"
    "ABDPEL"
    "ABDPL"
    "ABD_PEL"
    "ABD_PELVIS"
    "CHEST_ABD"
    "CHEST_ABDOMEN"
    "CHEST_ABD_PELV"
    "CHEST_TO_PELVIS"
    "CH_AB_PEL"
    "CST_ABD_PEL"
    "CAP"
    "CAP_W"
    "C_A_P"
    "NECK_CHEST_ABD"
    "CT_ABDOMEN_PELVIS_W"
    "CTA_ABD_AORTA_RU"
    "LIVER_GALLBLADDE"
    "TORSO"
    "GASTRO"
    "COLON"
  )

  for str in "${aliases[@]}"; do
    if [ "$str" = "$in_name" ]; then
      true
      return
    fi
  done

  false
  return
}

function is_chest() {
  in_name="$1"
  aliases=("CHEST_WITHOUT"
    "CHEAT"
    "CHST"
    "CHEST"
    "CHEST_ABD"
    "CHEST_ABDOMEN"
    "CHEST_ABD_PELV"
    "CHEST_TO_PELVIS"
    "CH_AB_PEL"
    "CST_ABD_PEL"
    "CAP"
    "CAP_W"
    "C_A_P"
    "CTA_CHEST"
    "NECK_CHEST_ABD"
    "HEART"
    "PE_CHEST"
    "TORSO")

  for str in "${aliases[@]}"; do
    if [ "$str" = "$in_name" ]; then
      true
      return
    fi
  done

  false
  return
}

function is_aorta() {
  in_name="$1"
  aliases=("AORTA"
    "CTA_ABD_AORTA_RU"
    "THORACIC_AORTA")

  for str in "${aliases[@]}"; do
    if [ "$str" = "$in_name" ]; then
      true
      return
    fi
  done

  false
  return
}

function is_pelvis() {
  in_name="$1"
  aliases=("CERVIX"
    "CHEST_ABD_PELV"
    "CHEST_TO_PELVIS"
    "CH_AB_PEL"
    "CST_ABD_PEL"
    "CAP"
    "CAP_W"
    "C_A_P"
    "GU"
    "CT_ABDOMEN_PELVIS_W"
    "PELVIS"
    "KIDNEY_URETER_BL")

  for str in "${aliases[@]}"; do
    if [ "$str" = "$in_name" ]; then
      true
      return
    fi
  done

  false
  return
}

function is_extremity() {
  in_name="$1"
  aliases=("EXTREMITY"
    "SHOULDER"
    "CTA_RUNOFF"
    "VESSEL")

  for str in "${aliases[@]}"; do
    if [ "$str" = "$in_name" ]; then
      true
      return
    fi
  done

  false
  return
}

function is_headandneck() {
  in_name="$1"
  aliases=("CSPINE"
    "NECK"
    "NECK_CHEST_ABD"
    "HEAD"
    "HEAD_NECK")

  for str in "${aliases[@]}"; do
    if [ "$str" = "$in_name" ]; then
      true
      return
    fi
  done

  false
  return
}

function is_other() {
  in_name="$1"
  aliases=("OTHER"
    "UNKNOWN"
    "RUNOFF")

  for str in "${aliases[@]}"; do
    if [ "$str" = "$in_name" ]; then
      true
      return
    fi
  done

  false
  return
}

function is_spine() {
  in_name="$1"
  aliases=("SPINE"
    "CSPINE"
    "LSPINE"
    "LUMBAR_SPINE"
    "TSPINE")

  for str in "${aliases[@]}"; do
    if [ "$str" = "$in_name" ]; then
      true
      return
    fi
  done

  false
  return
}

# merge body parts
function frankenstein() {
  in_part="$1"

  if is_abdomen $in_part; then
    echo "ABDOMEN"
    return
  elif is_chest $in_part; then
    echo "CHEST"
    return
  elif is_aorta $in_part; then
    echo "AORTA"
    return
  elif is_pelvis $in_part; then
    echo "PELVIS"
    return
  elif is_extremity $in_part; then
    echo "EXTREMITY"
    return
  elif is_headandneck $in_part; then
    echo "HEADANDNECK"
    return
  elif is_other $in_part; then
    echo "OTHER"
    return
  elif is_spine $in_part; then
    echo "SPINE"
    return
  else
    echo "$in_part"
    return
  fi

}

# empty string -> NA
# replace commas with underscores
function clean_value() {
  val="$1"
  if [ "$val" = "" ]; then
    val="NA"
  fi
  
  val=${val//,/_} 
  
  echo $val
  return
}


function write_row() {
  val=$(clean_value "$9")
  if [ "$val" != "NA" ]; then
    echo "$2,$3,$4,$5,$6,$7,$8,$val" >> $1
  fi
  return
} 

function write_dicom_rows() {

  ofile="$1"
  pmbbid="$2"
  studyuid="$3"
  acc="$4"
  series_number="$5"
  series_name="$6"
  tfile="$7"

  body=`cat $tfile | grep -a "(0018,0015)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  mod=`cat $tfile | grep  -a "(0008,0060)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  code=`cat $tfile | grep -a -A 6 "(0008,1032)" | grep "(0008,0100)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  codename=` cat $tfile | grep -a -A 6 "(008,1032)" | grep "(0008,0104)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs` 
  acc=`cat $tfile | grep  -a "(0008,0050)" | sed -n 1p | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  date=`cat $tfile | grep  -a "(0008,0021)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  stime=`cat $tfile | grep  -a "(0008,0031)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  manu=`cat $tfile | grep -a "(0008,0070)" | head -n 1 | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  sex=`cat $tfile | grep  -a "(0010,0040)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  stud=`cat $tfile | grep  -a "(0008,1030)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  model=`cat $tfile | grep  -a "(0008,1090)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  stamp="${date}${stime}"
  body_brief=$(frankenstein $body)


  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name NA SeriesTimestamp "$stamp"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x0021 SeriesDate "$date"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x0031 SeriesTime "$stime"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x0070 Manufacturer "$manu"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x1090 ModelName "$model"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x1030 StudyDescription "$stud"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0015 BodyPartExamined "$body"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name NA BodyPart "$body_brief"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0010x0040 PatientsSex "$sex"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x0060 Modality "$mod"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x1032_0008x0100 ProcedureCode "$code"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x1032_0008x0104 ProcedureCodeMeaning "$codename"

  return
}

function write_image_rows() {
 
  ofile="$1"
  pmbbid="$2"
  studyuid="$3"
  acc="$4"
  series_number="$5"
  series_name="$6"
  tfile="$7"

  rows=`cat $tfile | grep  -a "(0028,0010)" | cut -d " " -f3 | xargs`
  cols=`cat $tfile | grep  -a "(0028,0011)" | cut -d " " -f3 | xargs`
  lowpix=`cat $tfile | grep  -a "(0028,0106)" | cut -d " " -f3 | xargs`
  bigpix=`cat $tfile | grep  -a "(0028,0107)" | cut -d " " -f3 | xargs`
  thickness=`cat $tfile | grep  -a "(0018,0050)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  between=`cat $tfile | grep  -a "(0018,0088)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  spacing_x=`cat $tfile | grep  -a "(0028,0030)" | cut -d "[" -f2 | cut -d "]" -f1 | cut -d '\\' -f1 | xargs`
  spacing_y=`cat $tfile | grep  -a "(0028,0030)" | cut -d "[" -f2 | cut -d "]" -f1 | cut -d '\\' -f2 | xargs`
  in_acq=`cat $tfile | grep  -a "(0020,1002)" | cut -d " " -f3 | xargs`  
  itype=`cat $tfile | grep  -a "(0008,0008)" | cut -d "[" -f2 | cut -d "]" -f1`
  
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0008x0008 ImageType "${itype}" 
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x0010 Rows "$rows"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x0011 Cols "$cols"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x0030[0] PixelSpacingX "$spacing_x"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x0030[1] PixelSpacingY "$spacing_y"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x0106 LowestPixelValue "$lowpix"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x0107 HighestPixelValue "$bigpix"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0050 SliceThickness "$thickness"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0088 SpacingBetweenSlices "$between" 
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0020x1002 ImagesInAcquisition "$in_acq"

  return

}

# Get values specific to Contrast/Bolus use
function write_contrast_rows() {

  ofile="$1"
  pmbbid="$2"
  studyuid="$3"
  acc="$4"
  series_number="$5"
  series_name="$6"
  tfile="$7"

  agent=`cat $tfile | grep  -a "(0018,0010)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  route=`cat $tfile | grep  -a "(0018,1040)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  volume=`cat $tfile | grep  -a "(0018,1041)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  start_time=`cat $tfile | grep  -a "(0018,1042)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  stop_time=`cat $tfile | grep  -a "(0018,1043)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  dose=`cat $tfile | grep  -a "(0018,1044)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  rate=`cat $tfile | grep  -a "(0018,1046)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  duration=`cat $tfile | grep  -a "(0018,1047)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  ingredient=`cat $tfile | grep  -a "(0018,1048)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  concentration=`cat $tfile | grep  -a "(0018,1049)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`

  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0010 ContrastBolusAgent "$agent"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0040 ContrastBolusRoute "$route"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1041 ContrstBolusVolume "$volume"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1042 ContrastBolusStartTime "$start_time"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1043 ContrastBolusStopTime "$stop_time"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1044 ContrastBolusTotalDose "$does"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1046 ContrastBolusRate "$rate"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1047 ContrastBolusDuration "$duration"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1048 ContrastBolusIngredient "$ingredient"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1049 ContrastBolusIngredientConcentration "$concentration"

  return

}

# Get values specific to CT data
function write_ct_rows() {

  ofile="$1"
  pmbbid="$2"
  studyuid="$3"
  acc="$4"
  series_number="$5"
  series_name="$6"
  tfile="$7"

  kvp=`cat $tfile | grep  -a "(0018,0060)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  exposure=`cat $tfile | grep  -a "(0018,1152)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  conv=`cat $tfile | grep  -a "(0018,1210)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  intercept=`cat $tfile | grep  -a "(0028,1051)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  slope=`cat $tfile | grep  -a "(0028,1053)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  restype=`cat $tfile | grep  -a "(0028,1054)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`

  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0060 KVP "$kvp"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1152 Exposure "$exposure"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1210 ConvolutionKernel "$conv"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x1053 RescaleSlope "$slope"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x1051 RescaleIntercept "$intercept"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0028x1054 RescaleType "$restype"

  return

}

function write_mr_rows() {

  ofile="$1"
  pmbbid="$2"
  studyuid="$3"
  acc="$4"
  series_number="$5"
  series_name="$6"
  tfile="$7"

  rept=`cat $tfile | grep  -a "(0018,0080)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  echot=`cat $tfile | grep  -a "(0018,0081)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  invt=`cat $tfile | grep  -a "(0018,0082)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  navg=`cat $tfile | grep  -a "(0018,0083)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  freq=`cat $tfile | grep  -a "(0018,0084)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  nucl=`cat $tfile | grep  -a "(0018,0085)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  field=`cat $tfile | grep  -a "(0018,0087)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  rcoil=`cat $tfile | grep  -a "(0018,1250)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  tcoil=`cat $tfile | grep  -a "(0018,1251)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  tpos=`cat $tfile | grep  -a "(0020,0105)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
  tres=`cat $tfile | grep  -a "(0020,0110)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`

  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0080 RepetitionTime "$rept"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0081 EchoTime "$echot"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0082 InversionTime "$invt"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0083 NumberOfAverages "$navg"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0084 ImagingFrequency "$freq"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0085 ImagedNucleus "$nucl"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x0087 MagneticFieldStrength "$field"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1250 ReceiveCoilName "$rcoil"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0018x1251 TransmitCoilName "$tcoil"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0020x0105 NumberOfTemporalPositions "$tpos"
  write_row $ofile $pmbbid $studyuid $acc $series_number $series_name 0020x0110 TemporalResolution "$tres"

  return

}

function write_us_rows() {

  ofile="$1"
  pmbbid="$2"
  studyuid="$3"
  acc="$4"
  series_number="$5"
  series_name="$6"
  tfile="$7"

  return
}

function write_pet_rows() {

  ofile="$1"
  pmbbid="$2"
  studyuid="$3"
  acc="$4"
  series_number="$5"
  series_name="$6"
  tfile="$7"

  return
}



function is_image() {
  mod="$1"
  img=1
  if [ "$mod" = "SR" ]; then
    img=0
  fi
  echo $img
  return
}


dir="$1"
tdir="$2"
index="$3"
studies="$4"

offset=$SLURM_ARRAY_TASK_ID

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
#echo $sub_line

# get subdirectory to summarize
subdir=$(echo $sub_line | xargs)
subdir_name=`basename $subdir`
#echo "Subdir: $subdir_name"


#module load dcmtk
export DCMDICTPATH=/cbica/projects/pmbb-vision/pkg/dcmtk-3.6.8-linux-x86_64-static/share/dcmtk-3.6.8/dicom.dic
dcmdump="/cbica/projects/pmbb-vision/pkg/dcmtk-3.6.8-linux-x86_64-static/bin/dcmdump"
key="PMBB${subdir_name}"

for line in `cat ${studies} | grep ${key}`; do
  #echo $line
  pmbbid=$(echo $line | cut -d "," -f1)
  studyuid=$(echo $line | cut -d "," -f2)
  
  d1=${pmbbid:4:4}
  d2=${pmbbid:8:4}

  studydir="${subdir}/${d2}/${pmbbid}/${studyuid}"
  echo "Studydir: $studydir"  
  serieslist=$(ls -d $studydir/*)
  series_number="NA"
  series_name="NA"
  nfiles=0

  #echo $serieslist


  for series in $serieslist; do
    #echo $series
    series_name_full=$(basename $series)

    if [ "$series_name_full" == "Diagnostic" ]; then
      date=`cat $tfile | grep  -a "(0008,0021)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
      series_number="NA"
      series_name="Diagnostic-Report"
      nfiles=$(ls ${subdir}/${d2}/${pmbbid}/${studyuid}/Diagnostic*/*.dcm 2> /dev/null | wc | xargs | cut -d " " -f1)
    elif [ "$series_name_full" == "Diagnostic-Report" ]; then
      series_number="NA"
      series_name="Diagnostic-Report"
      nfiles=$(ls ${subdir}/${d2}/${pmbbid}/${studyuid}/Diagnostic*/*.dcm 2> /dev/null | wc | xargs | cut -d " " -f1) 
    else
      series_number=$(echo $series_name_full | cut -d "-" -f1)
      series_name=$(echo $series_name_full | cut -d "-" -f 2-)
      nfiles=0
      nfiles=$(ls $series/*.dcm 2> /dev/null | wc | xargs | cut -d " " -f1)
    fi

    if [ -e "$series" ]; then
      sz=$(du -d 0 $series | cut -f1)

      firstfile=$(ls $series/*.dcm | head -n 1)
      tfile=`mktemp -p ${tdir}/`

      $dcmdump $firstfile | grep -v "(no value available)" | grep -v "(standard input)" > $tfile
      ofile="${tdir}/${subdir_name}_series.csv"

      if [ "${series_number}" = "NA" ]; then
        series_number=`cat $tfile | grep  -a "(0020,0011)" | cut -d "[" -f2 | cut -d "]" -f1 | xargs`
      fi
      if [ "{series_number}" = "" ]; then
        series_number="NA"
      fi


      # Info not in dicom files
      write_row $ofile $pmbbid $studyuid $acc $series_number $series_name NA NumberOfFiles $nfiles
      write_row $ofile $pmbbid $studyuid $acc $series_number $series_name NA StorageSize $sz

      # Tags for all dicom data
      write_dicom_rows $ofile $pmbbid $studyuid $acc $series_number $series_name $tfile

      # Tags for contrast/bolus use
      write_contrast_rows $ofile $pmbbid $studyuid $acc $series_number $series_name $tfile

      # Tags common to all image modalities
      image=$(is_image $mod)
      if [ $image -eq 1 ]; then
        write_image_rows $ofile $pmbbid $studyuid $acc $series_number $series_name $tfile
      fi
      
      # Tags specific to CT images
      if [ "$mod" = "CT" ]; then
         write_ct_rows $ofile $pmbbid $studyuid $acc $series_number $series_name $tfile
      fi
   
      # Tags specific to MR images
      if [ "$mod" = "MR" ]; then
         write_mr_rows $ofile $pmbbid $studyuid $acc $series_number $series_name $tfile
      fi

      # Tags speicific to US images
      if [ "$mod" = "US" ]; then
         write_us_rows $ofile $pmbbid $studyuid $acc $series_number $series_name $tfile
      fi

      # Tags specific to PET images
      if [ "$mod" = "PT" ]; then
         write_pet_rows $ofile $pmbbid $studyuid $acc $series_number $series_name $tfile
      fi

      rm $tfile
    fi

   
  done

done



