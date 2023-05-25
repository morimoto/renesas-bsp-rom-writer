#! /bin/bash

SREC=$@

for srec in ${SREC}
do
	data=`head -n 2 ${srec} | tail -n 1`
	echo "${data:4:8} : ${srec}"
done
