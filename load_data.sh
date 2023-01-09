#!/bin/bash
for entry in "/Users/dcoleyoung/Documents/Horse/"*/
do
  x=`basename $entry` 
  y="$entry/$x"
  echo "Trying $entry"
  `python drf_reader2.py $y --results` 
  echo "Processed $entry"
done
