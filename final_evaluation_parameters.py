import pandas as pd

# Define column names
column_names = ["question", "expected_answer", "generated_answer", "Precision", "Recall", "F1"]

# Load the CSV file without a header and assign column names
file_path = "logging/log_queries.csv"
df = pd.read_csv(file_path, names=column_names, header=None)

# Compute the averages
avg_precision = df["Precision"].mean()
avg_recall = df["Recall"].mean()
avg_f1 = df["F1"].mean()

# Print the results
print(f"Average Precision: {avg_precision:.4f}")
print(f"Average Recall: {avg_recall:.4f}")
print(f"Average F1-score: {avg_f1:.4f}")
