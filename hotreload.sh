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

if [[ ! "$filename" =~ \.py$ ]]; then
    echo "Error: File '$filename' is not a Python file (.py extension required)"
    exit 1
fi

python "$filename"

inotifywait -e close_write,moved_to,create -m . |
while read -r directory events changed_file; do
  if [ "$changed_file" = "$filename" ]; then
    python "$filename"
  fi
done
