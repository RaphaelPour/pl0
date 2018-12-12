#!/bin/bash

for filename in tmin*.cl0; do
	echo Compile $filename
	../../P/vm "$filename"
done
