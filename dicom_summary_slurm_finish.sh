#!/bin/bash

tdir="$1"
output="$2"

id_file="${output}_pmbbvid.txt"
echo "PPMBVID" > $id_file
cat ${tdir}/*_pmbbvid.txt >> $id_file

report_file="${output}_reports.txt"
echo "ReportDirectory" > $report_file
cat ${tdir}/*_reports.txt >> $report_file

study_file="${output}_studies.csv"
echo "PMBBVID,StudyUID" > $study_file
cat ${tdir}/*_studies.csv >> $study_file

rm -f ${tdir}/*_pmbbvid.txt
rm -f ${tdir}/*_reports.txt
rm -f ${tdir}/*_studies.csv
