import json

# File path
file_path = "ragas_implementation_on_general_set/log_queries2.json"

# Load the JSON file
with open(file_path, "r") as file:
    data = json.load(file)  # Read the JSON content

# Check if the data is a list of dictionaries
sum1 = 0
sum2 = 0
sum3 = 0
sum4 = 0
if isinstance(data, list):
    for item in data:
        if item['eval']['answer_correctness'] == "N/A":
            item['eval']['answer_correctness'] = 0
        if item['eval']['faithfulness'] == "N/A":    
            item['eval']['faithfulness'] = 0
        if item['eval']['context_recall'] == "N/A":
            item['eval']['context_recall'] = 0
        if item['eval']['semantic_similarity'] == "N/A":
            item['eval']['semantic_similarity'] = 0
        sum1 += item['eval']['answer_correctness']
        sum2 += item['eval']['faithfulness']
        sum3 += item['eval']['context_recall']
        sum4 += item['eval']['semantic_similarity']
else:
    print("JSON file does not contain a list of dictionaries.")

print(sum1/len(data))
print(sum2/len(data))
print(sum3/len(data))
print(sum4/len(data))
