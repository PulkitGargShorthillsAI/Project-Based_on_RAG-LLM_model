import json
import pandas as pd

# Load the JSON file
json_filename = "ragas_implementation/log_queries2.json"
csv_filename = "ragas_implementation/evaluation_results.csv"

with open(json_filename, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract relevant fields into a list of dictionaries
rows = []
for item in data:
    rows.append({
        "context_recall": item["eval"].get("context_recall", ""),
        "faithfulness": item["eval"].get("faithfulness", ""),
        "semantic_similarity": item["eval"].get("semantic_similarity", ""),
        "answer_correctness": item["eval"].get("answer_correctness", "")
    })

# Convert to DataFrame
df = pd.DataFrame(rows)

# Save to CSV
df.to_csv(csv_filename, index=False)

print(f"CSV saved successfully as {csv_filename}!")
