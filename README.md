# ADAR-Sensor-Analysis
Code for analysis in Kim et al., 'Precision targeting of C3+ reactive astrocyte subpopulation with endogenous ADAR in iPSC-derived model"

FASTQ Sequence Search Tool
Overview
This Python script is designed to efficiently search for one or more sets of target DNA/RNA sequences within a directory of gzipped FASTQ (.fastq.gz) files. It identifies records containing the specified sequences (or their reverse complements) and saves the full matching records (header and sequence) to separate output files for easy analysis.

This tool is useful for quickly filtering large sequencing datasets to find reads that contain specific adapter sequences, genetic markers, or other sequences of interest.

Key Features
Multiple Target Groups: Search for several distinct sets of sequences simultaneously. Results for each group are saved to a separate file.

Reverse Complement Matching: The script automatically searches for both the provided sequence and its reverse complement, so you don't have to specify both.

Case-Insensitive: The search is case-insensitive, accommodating variations in sequence data.

Batch Processing: Automatically processes all .fastq.gz files located within a specified input directory.

Easy Configuration: No command-line arguments needed. Simply edit the variables in the "USER-CONFIGURABLE SECTION" at the top of the script to set your target sequences and I/O directories.

Requirements
Python 3

BioPython

You can install the required library using pip:

pip install biopython

How to Use
Clone or download the script.

Configure the script: Open the .py file in a text editor and modify the following variables in the USER-CONFIGURABLE SECTION:

TARGETS_1, TARGETS_2, etc.: Define your sequence(s) of interest in these sets.

INPUT_DIRECTORY: Set the path to the folder containing your .fastq.gz files.

OUTPUT_DIRECTORY: Set the path where the result files will be saved. The directory will be created if it doesn't exist.

Run the script from your terminal:

python your_script_name.py

Check the results: The script will generate .txt files in your specified output directory. Each file will contain the FASTA-formatted records that matched the corresponding target group.
