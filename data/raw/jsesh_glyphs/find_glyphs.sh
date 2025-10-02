#!/bin/bash

# An array containing all the Gardiner codes from your list.
codes=(
    "N5" "R11" "D10" "F34" "U6" "A2" "L1" "S34"
    "E16" "E17" "B1" "E13" "G31" "E1" "E23" "I10" "I12" "I3" "I4"
    "G5" "E4" "C9" "G26" "C3" "C2" "C10" "C20" "A40" "C1" "C12"
    "P1" "P4" "E22" "E20" "E24" "E25" "G1" "G14" "H6" "N27" "N11"
    "N30" "N1" "C23" "V9" "N14" "G29" "G53" "V10" "S38" "S42" "S4"
    "S5" "S45" "D28" "O25" "R3" "R4" "R7" "O24" "S3" "V31" "V37"
    "F36" "Q1" "Q3" "V36" "V39" "S39" "S40" "S1" "M1" "M9" "N35"
)

# Start building the 'find' regex pattern.
# We'll use a single pattern with OR conditions for all codes.
# `find -E` enables extended regex, which is standard on macOS.
find_regex_pattern=".*("
first_code=true
for code in "${codes[@]}"; do
    if [ "$first_code" = true ]; then
        find_regex_pattern+="US22${code}[A-Z]?\.svg"
        first_code=false
    else
        find_regex_pattern+="|US22${code}[A-Z]?\.svg"
    fi
done
find_regex_pattern+=")$"

# Execute the final, single 'find' command.
find -E . -type f -regex "$find_regex_pattern" | sort -u
