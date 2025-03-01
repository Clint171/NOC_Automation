input_file = "devices/routers-prod.csv"
output_file = "formatted_file.csv"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        first_string = line.split()[0]  # Get only the first string
        outfile.write(first_string + "\n")

print("Formatting complete. Check 'formatted_file.csv'.")
