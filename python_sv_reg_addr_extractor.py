def create_dictionary_from_file(input_file_path, output_file_path):
    # Read the input file and create the dictionary
    dictionary = {}
    with open(input_file_path, 'r') as file:
        for line in file:
            # Remove any leading/trailing whitespace and the newline character
            line = line.strip()
            if line:
                # Split the line into key and value
                key, value = line.split(':')
                dictionary[value.strip()] = key.strip()

    # Write the dictionary to the output .py file
    with open(output_file_path, 'w') as file:
        file.write('dictionary = {\n')
        for key, value in dictionary.items():
            file.write(f"    '{key}': '{value}',\n")
        file.write('}\n')

# Example usage
input_file = 'tc_reg_to_addr.txt'  # replace with your input file path
output_file = 'tc_reg_to_addr.py'  # replace with your desired output file path
create_dictionary_from_file(input_file, output_file)
