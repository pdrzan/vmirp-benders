#!/bin/bash

# --- Configuration ---
# Path to the main.py script
# Adjust this if your script is in a different location (e.g., "main.py")
MAIN_SCRIPT="main.py"

# Base directories
INSTANCES_DIR="instances"
RESULTS_DIR="results"

# --- Argument Check ---
if [ "$1" != "-t" ] || [ -z "$2" ]; then
    echo "Usage: $0 -t <time_limit_in_seconds>"
    echo "Example: ./run_batch.sh -t 30"
    exit 1
fi

TIME_LIMIT=$2

echo "Starting batch processing with time limit: $TIME_LIMIT seconds"

# --- Main Logic ---

# Define the sizes to iterate over
SIZES=(5 10 15 20 25)

# Check if the instances directory exists
if [ ! -d "$INSTANCES_DIR" ]; then
    echo "Error: Instances directory '$INSTANCES_DIR' not found."
    exit 1
fi

# Find all subdirectories in the instances folder
# Using find is safer than a simple glob for folder names with spaces


for SIZE in "${SIZES[@]}"; do
    find "$INSTANCES_DIR" -mindepth 1 -maxdepth 1 -type d | while read -r FOLDER_PATH; do
    # Get just the folder name (e.g., "Instances_highcost_H3")
    FOLDER_NAME=$(basename "$FOLDER_PATH")
    
    echo ""
    echo "--- Processing Directory: $FOLDER_NAME ---"
    
    # ---
    # NOTE: Your main.py script already handles creating the results
    # directory and writing the output file. 
    # This shell script just needs to find the files and call main.py.
    # ---
        for I in {1..5}; do
            # Construct the full path to the instance file
            INSTANCE_FILE="$FOLDER_PATH/abs${I}n${SIZE}.dat"
            
            # Check if the specific instance file exists
            if [ -f "$INSTANCE_FILE" ]; then
                echo "Processing $INSTANCE_FILE..."
                
                # Call the main.py script with the instance file and time limit
                # main.py will handle optimization and writing the result file
                python "src/$MAIN_SCRIPT" -i "$INSTANCE_FILE" -t "$TIME_LIMIT"
            else
                # Optional: Uncomment to see which files are skipped
                # echo "Skipping non-existent file: $INSTANCE_FILE"
                : # Bash no-op
            fi
        done
    done
done

echo ""
echo "--- Batch processing complete. ---"