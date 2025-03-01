import re

input_file = "formatted_file.csv"
output_file = "separated_file.csv"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        line = line.strip()
        modified_line = re.sub(r'_(?=[^_]+$)', ',', line)  # Replace the last underscore with a comma
        outfile.write(modified_line + "\n")

print("Separation complete. Check 'separated_file.csv'.")
