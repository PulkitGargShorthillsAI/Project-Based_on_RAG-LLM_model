import pandas as pd
from rag_pipeline import rag_chain
import time

# Load the CSV file without headers and assign column names
file_path = "log1.csv"  # Replace with your file path
df = pd.read_csv(file_path, header=None, names=["question", "answer"])

# Filter rows where 'question' contains the word 'visa' (case insensitive)
df_filtered = df[df['question'].str.contains('visa', case=False, na=False)]

# Modify the corresponding answers
for index in df_filtered.index:
    print(f"Question: {df.loc[index, 'question']}")
    response = rag_chain.invoke({"input": df.loc[index, 'question']})
    time.sleep(5)
    df.loc[index, 'answer'] = str(response['answer'])

# Save the updated CSV file
df.to_csv("updated_file.csv", index=False)
print("CSV file updated successfully!")
