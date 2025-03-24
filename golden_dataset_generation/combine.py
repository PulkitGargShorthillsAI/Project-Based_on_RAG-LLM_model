# import json

# # List of JSON files
# json_files = ["qa_output1.json", "qa_output2.json", "qa_output3.json"]

# merged_data = []

# for file in json_files:
#     with open(file, "r", encoding="utf-8") as f:
#         data = json.load(f)
        
#         if isinstance(data, list):
#             merged_data.extend(data)  # Append lists
#         else:
#             print(f"Skipping {file}, not a list!")

# # Save merged JSON
# with open("merged.json", "w", encoding="utf-8") as f:
#     json.dump(merged_data, f, indent=4)

# print("Merged JSON saved successfully!")



import json

# Load the JSON file
json_filename = "merged.json"  # Change filename as needed

with open(json_filename, "r", encoding="utf-8") as f:
    data = json.load(f)

# Check if it's a list and count elements
if isinstance(data, list):
    print(f"Total elements in {json_filename}: {len(data)}")
else:
    print(f"Error: {json_filename} does not contain a list!")
