#!/bin/bash

# Clean up ALL previous files
rm -f validation_status.txt p4_validation_errors.txt temp_errors.txt error_summary.txt

# Function to validate P4 code and return error messages
validate_p4() {
    local p4_file=$1
    local attempt="$2"
    echo "Validating $p4_file..."
    
    # Create a temporary file for error output
    local error_file="p4_validation_errors.txt"
    
    # Run p4c compiler locally and capture all output
    p4c --std p4-16 $p4_file 2>&1 | tee $error_file
    local validation_status=${PIPESTATUS[0]}
    
    if [ $validation_status -eq 0 ]; then
        echo "✅ Validation successful: $p4_file"
        echo "SUCCESS" > validation_status.txt
        return 0
    else
        echo "❌ Validation failed: $p4_file"
        echo "VALIDATION_ERROR" > validation_status.txt
        extract_error_info "$attempt"
        return 1
    fi
}

# Function to extract relevant error information
extract_error_info() {
    local attempt="$1"
    local error_file="p4_validation_errors.txt"
    local error_history="error_summary.txt"
    
    # Create new error_summary.txt for this run
    if [ ! -f "$error_history" ]; then
        echo "=== P4 Code Validation Error History ===" > "$error_history"
    fi
    
    if [ -f "$error_file" ]; then
        # Append new error section with the current attempt number
        echo -e "\n=== Attempt $attempt Errors ===" >> "$error_history"
        echo "Timestamp: $(date)" >> "$error_history"
        echo "----------------------------------------" >> "$error_history"
        
        # Extract error messages
        grep -E "error:|warning:|syntax error" "$error_file" > temp_errors.txt
        if [ -s temp_errors.txt ]; then
            cat temp_errors.txt >> "$error_history"
        else
            echo "No specific error messages found in compiler output." >> "$error_history"
            echo "Full compiler output:" >> "$error_history"
            cat "$error_file" >> "$error_history"
        fi
        rm -f temp_errors.txt
    fi
}

# Main script
echo "P4 Code Validator"
echo "----------------"

# Get the attempt number from command line argument, default to 1
attempt="${1:-1}"

# Validate only test.p4 file
if [ -f "test.p4" ]; then
    validate_p4 "test.p4" "$attempt"
else
    echo "Error: test.p4 file not found"
    echo "VALIDATION_ERROR" > validation_status.txt
    exit 1
fi 