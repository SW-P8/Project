#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

filename="$1"

if [ ! -f "$filename" ]; then
    echo "Error: File '$filename' not found"
    exit 1
fi

inotifywait -e close_write,moved_to,create -m . |
while read -r directory events changed_file; do
  if [ "$changed_file" = "$filename" ]; then
    ./"$filename"
  fi
done
