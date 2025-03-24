# import pandas as pd

# # Define column names
# column_names = ["question", "expected_answer", "generated_answer", "Precision", "Recall", "F1","CS"]

# # Load the CSV file without a header and assign column names
# file_path = "logging/log_queries1.csv"
# df = pd.read_csv(file_path, names=column_names, header=None)

# # Compute the averages
# avg_precision = df["Precision"].mean()
# avg_recall = df["Recall"].mean()
# avg_f1 = df["F1"].mean()
# avg_cs = df['CS'].mean()

# # Print the results
# print(f"Average Precision: {avg_precision:.4f}")
# print(f"Average Recall: {avg_recall:.4f}")
# print(f"Average F1-score: {avg_f1:.4f}")
# print(f"Average Cosine Similarity: {avg_cs:.4f}")






import pandas as pd

# Define column names
column_names = ["question", "expected answer", "generated answer", "P", "R", "F1","CS","NE","NN","NC"]

# Load the CSV file without a header and assign column names
file_path = "updated_data.csv"
df = pd.read_csv(file_path, names=column_names, header=None)

# Compute the averages
avg_precision = df["P"].mean()
avg_recall = df["R"].mean()
avg_f1 = df["F1"].mean()
avg_cs = df['CS'].mean()
avg_ne = df['NE'].mean()
avg_nn = df['NN'].mean()
avg_nc = df['NC'].mean()

# Print the results
print(f"Average Precision: {avg_precision:.4f}")
print(f"Average Recall: {avg_recall:.4f}")
print(f"Average F1-score: {avg_f1:.4f}")
print(f"Average Cosine Similarity: {avg_cs:.4f}")
print(f"Average NE: {avg_ne:.4f}")
print(f"Average NN: {avg_nn:.4f}")
print(f"Average NC: {avg_nc:.4f}")

