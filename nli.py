import pandas as pd
from transformers import pipeline
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "roberta-large-mnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()
 
# 4. Inference helper
def classify_nli(premise, hypothesis):
    inputs = tokenizer.encode_plus(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1).squeeze()
    labels = ['entailment', 'neutral', 'contradiction']
    pred_label = labels[torch.argmax(probs).item()]
    return probs.tolist()


# Load CSV file
csv_filename = "log_queries1.csv"


df = pd.read_csv(csv_filename, header=None)
df.columns = ["question", "expected answer", "generated answer", "P", "R", "F1", "cosine similarity"]

# Compute similarity and add to dataframe
df["NLI Entailment"] = df.apply(lambda row: classify_nli(str(row["expected answer"]), str(row["generated answer"]))[2], axis=1)
df["NLI Neutrality"] = df.apply(lambda row: classify_nli(str(row["expected answer"]), str(row["generated answer"]))[1], axis=1)
df["NLI Contradiction"] = df.apply(lambda row: classify_nli(str(row["expected answer"]), str(row["generated answer"]))[0], axis=1)
# Save the updated CSV
df.to_csv("updated_data.csv", index=False)

print("CSV updated successfully with headers and NLI similarity scores!")















# import pandas as pd
# from transformers import pipeline
# import csv

# # Load the NLI model
# nli_model = pipeline("text-classification", model="facebook/bart-large-mnli")

# def classify_nli(premise, hypothesis):
#     """Classifies the relationship between premise and hypothesis using NLI."""
#     result = nli_model(f"{premise} </s> {hypothesis}")
    
#     if not isinstance(result, list) or not result:  # Handle unexpected output
#         raise ValueError(f"Unexpected NLI model output: {result}")

#     # Convert the result into a dictionary with labels as keys
#     scores = {entry["label"]: entry["score"] for entry in result}
    
#     return scores.get("ENTAILMENT", 0), scores.get("CONTRADICTION", 0), scores.get("NEUTRAL", 0)

# # Input and output CSV file names
# input_csv = "log_queries1.csv"
# output_csv = "updated_data.csv"

# # Read the CSV file **row by row**
# with open(input_csv, "r", newline="", encoding="utf-8") as infile, \
#      open(output_csv, "w", newline="", encoding="utf-8") as outfile:
    
#     reader = csv.reader(infile)
#     writer = csv.writer(outfile)

#     # Read the first row to check if headers exist
#     headers = next(reader, None)
    
#     # If headers are missing, add default ones
#     if headers is None or len(headers) != 7:
#         headers = ["question", "expected answer", "generated answer", "P", "R", "F1", "cosine similarity"]
    
#     # Add new columns for NLI scores
#     headers.extend(["NLI Entailment", "NLI Contradiction", "NLI Neutrality"])
    
#     # Write headers to the new CSV
#     writer.writerow(headers)

#     # Process each row individually
#     for row in reader:
#         if len(row) != 7:  # Ensure correct number of columns
#             print(f"Skipping invalid row: {row}")
#             continue

#         question, expected_answer, generated_answer, p, r, f1, cosine_similarity = row
        
#         # Compute NLI scores
#         entailment, contradiction, neutrality = classify_nli(expected_answer, generated_answer)
        
#         # Write row with NLI scores to the new CSV
#         writer.writerow(row + [entailment, contradiction, neutrality])

#         print(f"Processed row: {question}")  # Optional progress log

# print("CSV updated successfully row by row!")
















# def compare_answers_nli(answer1, answer2):
#     """
#     Compares two answers using Natural Language Inference (NLI).

#     Args:
#         answer1: The first answer.
#         answer2: The second answer.

#     Returns:
#         The NLI confidence score for similarity.
#     """
#     classifier = pipeline("text-classification", model="facebook/bart-large-mnli")

#     hypothesis_comparison = f"The answer '{answer1}' is equivalent to '{answer2}'."
#     result_comparison = classifier(hypothesis_comparison)

#     similarity_score = next((item['score'] for item in result_comparison if item['label'] == "ENTAILMENT"), 0)

#     return similarity_score