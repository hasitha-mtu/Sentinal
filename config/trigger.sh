#!/bin/bash
INPUT_DIR="/path/to/input/files"
OUTPUT_DIR="/path/to/output/files"
GRAPH="/path/to/LandCoverClassification.xml"

for FILE in "$INPUT_DIR"/*.SAFE; do
    OUTPUT="$OUTPUT_DIR/$(basename "$FILE" .SAFE).tif"
    gpt $GRAPH -Pfile=$FILE -Poutput=$OUTPUT
done
