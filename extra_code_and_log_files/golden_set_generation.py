import json
import time
import os
import google.generativeai as genai
from google import genai
import json
import csv
import logging
from pydantic import BaseModel


genai.configure(api_key=os.getenv('GEMINI_API1'))


def read_file(file_path):
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
        

class QA(BaseModel):
    question: str
    answer: str
    expected_context:str
    question_type:str



client = genai.Client(api_key=os.getenv('GEMINI_API1'))

def generate_qa(text):
    prompt = f'''You are an expert dataset creator tasked with generating a high-quality golden dataset for evaluating a Retrieval-Augmented Generation (RAG) model.

Given the following document, generate a diverse set of questions along with their ground truth answers and the expected retrieval context (i.e., the passage or section of the document where the answer is found). Ensure that the questions cover multiple dimensions of complexity and robustness, including:

### Types of Questions:
1. **Fact-based questions** (Simple, direct queries such as Who, What, When, Where)
2. **Comparative questions** (Questions comparing entities or concepts, e.g., How is X different from Y?)
3. **Causal questions** (Questions exploring cause-effect relationships, e.g., Why did X happen?)
4. **Complex/multi-hop reasoning questions** (Questions requiring synthesis or multiple steps of reasoning)
5. **Edge cases and adversarial questions:**  
   - Questions that are ambiguous or may be interpreted in multiple ways  
   - Out-of-context or unanswerable questions  
   - Gibberish or illogical questions

For each question, generate a precise answer strictly based on the document and identify the exact passage (expected retrieval context) that supports the answer. For questions that are not answerable based on the document (e.g., out-of-context or gibberish queries), set the answer to:
"This question cannot be answered based on the given document." and leave the expected context field empty.

**Document:**  
{text}

### Instructions:
- Generate at least 5-10 questions per document, ensuring a balance across the categories mentioned above.
- Label each question with its type: "Fact-based", "Comparative", "Causal", "Complex", or "Edge Case".
- Provide a clear and concise ground truth answer that is strictly derived from the provided document.
- Extract and include the specific passage (or section) from the document that best supports the answer in the "expected_context" field.
- For invalid or unanswerable questions, set the answer to "This question cannot be answered based on the given document." and leave "expected_context" empty.

### Output Format (JSON):
```json
{{
    "questions": [
        {{
            "question": "<Generated Question>",
            "answer": "<Generated Answer>",
            "question_type": "<Fact-based | Comparative | Causal | Complex | Edge Case>",
            "expected_context": "<Passage from the document where the answer is found>"
        }},
        ...
    ]
}}
'''
    response = client.models.generate_content(model="gemini-2.0-flash",contents=prompt,config={'response_mime_type': 'application/json','response_schema': list[QA]})
    try:
        qa_pairs = json.loads(response.text)
        return qa_pairs if isinstance(qa_pairs, list) else []
    except json.JSONDecodeError:
        return []


output_json = "qa_output1.json"
output_csv = "qa_output1.csv"
folder_paths=["data1"]






# Configure logging
logging.basicConfig(
    filename="processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def load_progress(progress_file):
    """Load the set of processed files from a progress file."""
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_progress(progress_file, processed_files):
    """Save the set of processed files to a progress file."""
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(list(processed_files), f, indent=4)
    logging.info("Progress saved: %d files processed.", len(processed_files))

def save_qa_data(output_json, output_csv, all_qa):
    """Save the Q&A data to JSON and CSV files."""
    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(all_qa, json_file, indent=4, ensure_ascii=False)
    
    with open(output_csv, "w", encoding="utf-8", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Question", "Answer"])
        for qa in all_qa:
            writer.writerow([qa["question"], qa["answer"]])
    
    logging.info("Q&A data saved: %d pairs generated.", len(all_qa))

def process_folders(folder_paths, output_json, output_csv, progress_file="progress.json"):
    """Process files in given folders and generate Q&A pairs with checkpointing."""
    
    all_qa = []
    processed_files = load_progress(progress_file)  # Load previously processed files
    count = 0
    
    logging.info("Starting processing for folders: %s", ", ".join(folder_paths))
    
    for folder_path in folder_paths:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Skip if file was processed before or is not a valid document
            if filename in processed_files or not os.path.isfile(file_path) or not filename.endswith((".txt", ".pdf")):
                continue  

            logging.info("Processing file: %s from %s", filename, folder_path)
            print(f"Processing: {filename} from {folder_path}")
            
            try:
                text = read_file(file_path)
                qa_pairs = generate_qa(text)
                all_qa.extend(qa_pairs)
                processed_files.add(filename)  # Mark file as processed
                count += 1
                
                logging.info("Generated %d Q&A pairs for %s", len(qa_pairs), filename)
                print(f"Generated {len(qa_pairs)} Q&A pairs")
            except Exception as e:
                logging.error("Error processing %s: %s", filename, str(e))
                continue

            # Save progress every 10 files
            if count % 14 == 0:
                save_qa_data(output_json, output_csv, all_qa)
                save_progress(progress_file, processed_files)
                logging.info("Checkpoint reached: %d files processed. Waiting to avoid timeout.", count)
                print(f"Checkpoint saved: {count} files processed. Waiting to avoid timeout.")
                time.sleep(30)  # Delay to prevent API timeouts
    
    # Final save after all processing
    save_qa_data(output_json, output_csv, all_qa)
    save_progress(progress_file, processed_files)
    logging.info("Final save complete. Processed %d new files.", count)
    print(f"Final save complete. Processed {count} new files.")



process_folders(folder_paths, output_json, output_csv)



