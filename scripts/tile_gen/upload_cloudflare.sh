#!/usr/bin/env bash
set -e

AREA=$(basename "$(dirname "$PWD")")
VERSION=$(basename "$PWD")


if [[ $AREA != "planet" && $AREA != "monaco" ]]; then
  echo "Area must be 'planet' or 'monaco'. Terminating."
  exit 1
fi

if [ ! -f /data/ofm/config/rclone.conf ]; then
    echo "rclone.conf does not exist. Terminating."
    exit 1
fi


rm -f logs/rclone.log

rclone sync \
  --config=/data/ofm/config/rclone.conf \
  --transfers=8 \
  --multi-thread-streams=8 \
  --fast-list \
  -v \
  --stats-file-name-length 0 \
  --stats-one-line \
  --log-file logs/rclone.log \
  --exclude 'logs/**' \
  . "cf:ofm-$AREA/$VERSION"

