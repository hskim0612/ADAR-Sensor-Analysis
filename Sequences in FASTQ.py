# Import necessary libraries
from Bio import SeqIO
from Bio.Seq import Seq
import gzip
import os
import re

# --- USER-CONFIGURABLE SECTION ---

# Define the target sequences you want to search for.
# The script will also search for their reverse complements automatically.
TARGETS_1 = {"AAGAGAGACTATCGTGCCTaG", "TaGAAAATCGGTTCACTCCCA"}
TARGETS_2 = {"AAGAGAGACTATCGTGCCTGG", "TGGAAAATCGGTTCACTCCCA"}

# Specify the directories for input and output.
# IMPORTANT: Replace these placeholder paths with your actual directory paths.
# Example: 'C:/Users/YourUser/Desktop/fastq_data' or '/home/user/data/rnaseq'
INPUT_DIRECTORY = 'PATH_TO_YOUR_INPUT_DIRECTORY'
OUTPUT_DIRECTORY = 'PATH_TO_YOUR_OUTPUT_DIRECTORY'

# --- END OF USER-CONFIGURABLE SECTION ---


def get_target_sequences(sequences):
    """
    Converts target sequences to lowercase and creates a set including their reverse complements.
    This ensures the search is case-insensitive and finds matches on both strands.
    """
    sequences = {seq.lower() for seq in sequences}
    reverse_complements = {str(Seq(seq).reverse_complement()).lower() for seq in sequences}
    return sequences.union(reverse_complements)

def compile_pattern(sequences):
    """
    Compiles a regex pattern from a set of sequences for efficient searching.
    Each sequence is escaped to handle special characters correctly.
    """
    escaped_sequences = [re.escape(seq) for seq in sequences]
    pattern = re.compile('|'.join(escaped_sequences))
    return pattern

def main():
    """
    Main function to run the sequence search process.
    """
    # Ensure the output directory exists. If not, create it.
    if not os.path.exists(OUTPUT_DIRECTORY):
        print(f"Output directory not found. Creating directory: {OUTPUT_DIRECTORY}")
        os.makedirs(OUTPUT_DIRECTORY)

    # Prepare target sequences and regex patterns
    target_sequences_1 = get_target_sequences(TARGETS_1)
    target_sequences_2 = get_target_sequences(TARGETS_2)

    pattern_1 = compile_pattern(target_sequences_1)
    pattern_2 = compile_pattern(target_sequences_2)

    print(f"Starting to process files in: {INPUT_DIRECTORY}")

    # Process each FASTQ file in the input directory
    for filename in os.listdir(INPUT_DIRECTORY):
        if filename.endswith('.fastq.gz'):
            input_file_path = os.path.join(INPUT_DIRECTORY, filename)
            
            # Generate generic output file names
            base_name = filename.replace('.fastq.gz', '')
            output_file_path_1 = os.path.join(OUTPUT_DIRECTORY, f"{base_name}_matches_group1.txt")
            output_file_path_2 = os.path.join(OUTPUT_DIRECTORY, f"{base_name}_matches_group2.txt")

            try:
                # Open files for reading and writing
                with gzip.open(input_file_path, 'rt') as handle, \
                     open(output_file_path_1, 'w') as result_file_1, \
                     open(output_file_path_2, 'w') as result_file_2:

                    total_records = 0
                    found_1 = 0
                    found_2 = 0

                    for record in SeqIO.parse(handle, "fastq"):
                        total_records += 1
                        record_seq = str(record.seq).lower()

                        # Check for the first set of target sequences
                        if pattern_1.search(record_seq):
                            found_1 += 1
                            result_file_1.write(f">{record.id}\n")
                            result_file_1.write(record_seq + "\n")

                        # Check for the second set of target sequences
                        if pattern_2.search(record_seq):
                            found_2 += 1
                            result_file_2.write(f">{record.id}\n")
                            result_file_2.write(record_seq + "\n")
                
                print(f"Finished processing {filename}. Processed {total_records} records.")
                print(f"  - Found {found_1} matches for group 1.")
                print(f"  - Found {found_2} matches for group 2.")

            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")

    print("\nAll files processed.")

# This ensures the main function is called only when the script is executed directly
if __name__ == "__main__":
    main()
