#!/bin/bash

tdir="$1"
output="$2"

series_file="${output}_series.csv"
echo "PMBBVID,StudyUID,AccessionNumber,SeriesNumber,SeriesDescription,Tag,TagName,Value" > $series_file
cat ${tdir}/*_series.csv >> $series_file

for i in A B C D E F G H I J K L M N O P Q R S T U V W X Y Z; do
  echo "PMBBVID,StudyUID,AccessionNumber,SeriesNumber,SeriesDescription,Tag,TagName,Value" > ${output}_series_${i}.csv	
  cat $series_file | grep PMBB${i} >> ${output}_series_${i}.csv
done

#rm -Rf $tdir
