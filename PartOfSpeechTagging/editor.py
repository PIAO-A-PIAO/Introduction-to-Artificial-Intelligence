import os

# Open the input file for reading
input_file_path = os.path.join(os.path.dirname(__file__), 'training2.txt')
if not os.path.exists(input_file_path):
    print(f"Error: input file {input_file_path} not found")
    exit()
input_file = open(input_file_path)

# Read the lines from the input file
lines = input_file.read().splitlines()

# Open the output file for writing
output_file_path = os.path.join(os.path.dirname(__file__), 'test2.txt')
try:
    output_file = open(output_file_path, "w")
except IOError as e:
    print(f"Error: {e}")
    exit()

# Write the first element of each pair to the output file
for line in lines:
    pair = line.split(' : ')
    output_file.write(pair[0] + "\n")

# Close the files
input_file.close()
output_file.close()

print(f"Output file {output_file_path} created successfully.")

# if __name__ == '__main__':

#     import pickle

#     # Generate your dictionary
#     my_dict = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
#     dict_path = os.path.join(os.path.dirname(__file__), 'dict.txt')
#     # Open a file for writing binary data
#     with open(dict_path, 'wb') as f:
#         # Dump the dictionary to the file using pickle
#         pickle.dump(my_dict, f)
