#!/usr/bin/env bash

DATE=$(date +"%Y%m%d_%H%M%S")

RUN_FOLDER="/data/planetiler/runs/monaco_$DATE"

mkdir -p "$RUN_FOLDER"
cd "$RUN_FOLDER" || exit


# the Xmx value below the most important parameter here
# setting is less then 25g means there is too little memory
# setting it to too much means there is too much memory used

java -Xmx30g \
  -jar /data/planetiler/bin/planetiler.jar \
  `# Download the latest planet.osm.pbf from s3://osm-pds bucket` \
  --area=monaco --download \
  `# Accelerate the download by fetching the 10 1GB chunks at a time in parallel` \
  --download-threads=10 --download-chunk-size-mb=1000 \
  `# Also download name translations from wikidata` \
  --fetch-wikidata \
  --output=output.mbtiles \
  `# Store temporary node locations at fixed positions in a memory-mapped file` \
  --nodemap-type=array --storage=mmap \
  --force \
  > "output_$DATE.log" 2> "err_$DATE.log"



