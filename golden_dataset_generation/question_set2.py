import json
import time
import os
import logging
import csv
import google.generativeai as genai
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    filename="processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class QA(BaseModel):
    """Data model for storing a Q&A pair."""
    question: str
    answer: str
    expected_context: str
    question_type: str

class QAProcessor:
    """Handles the entire QA processing pipeline using Gemini API."""
    
    def __init__(self, api_key, output_json, output_csv, folder_paths):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.output_json = output_json
        self.output_csv = output_csv
        self.folder_paths = folder_paths
        self.progress_file = "progress.json"
        self.all_qa = []
        self.processed_files = self.load_progress()
    
    def load_progress(self):
        """Load the set of processed files from a progress file."""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def save_progress(self):
        """Save the processed files to a progress file."""
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(list(self.processed_files), f, indent=4)
        logging.info("Progress saved: %d files processed.", len(self.processed_files))

    def save_qa_data(self):
        """Save Q&A data to JSON and CSV files."""
        with open(self.output_json, "w", encoding="utf-8") as json_file:
            json.dump([qa.dict() for qa in self.all_qa], json_file, indent=4, ensure_ascii=False)

        with open(self.output_csv, "w", encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Question", "Answer", "Expected Context", "Question Type"])
            for qa in self.all_qa:
                writer.writerow([qa.question, qa.answer, qa.expected_context, qa.question_type])

        logging.info("Q&A data saved: %d pairs generated.", len(self.all_qa))

    def read_file(self, file_path):
        """Read and return content of text files."""
        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()

    def generate_qa(self, text):
        """Use Gemini API to generate Q&A pairs."""
        prompt = f'''
        You are an expert dataset creator tasked with generating a high-quality golden dataset for evaluating a Retrieval-Augmented Generation (RAG) model.

        Given the following document, generate a diverse set of questions with their ground truth answers and expected retrieval context.

        **Document:** {text}

        **Output Format (JSON):**
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
        response = self.model.generate_content(prompt, generation_config=genai.types.GenerationConfig(response_mime_type='application/json'))

        try:
            qa_pairs_raw = json.loads(response.text)
            if isinstance(qa_pairs_raw, dict) and 'questions' in qa_pairs_raw and isinstance(qa_pairs_raw['questions'], list):
                qa_pairs = [QA(**qa_data) for qa_data in qa_pairs_raw['questions']]
                return qa_pairs
            else:
                return []
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logging.error(f"Error parsing JSON response: {e}, Response text: {response.text}")
            return []

    def process_folders(self):
        """Processes all folders to generate Q&A pairs."""
        count = 0
        logging.info("Starting processing for folders: %s", ", ".join(self.folder_paths))

        for folder_path in self.folder_paths:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                if filename in self.processed_files or not os.path.isfile(file_path) or not filename.endswith(".txt"):
                    continue  

                logging.info("Processing file: %s", filename)
                print(f"Processing: {filename}")

                try:
                    text = self.read_file(file_path)
                    qa_pairs = self.generate_qa(text)
                    self.all_qa.extend(qa_pairs)
                    self.processed_files.add(filename)
                    count += 1
                    
                    logging.info("Generated %d Q&A pairs for %s", len(qa_pairs), filename)
                    print(f"Generated {len(qa_pairs)} Q&A pairs")
                except Exception as e:
                    logging.error("Error processing %s: %s", filename, str(e))
                    continue

                # Save progress every 10 files
                if count % 10 == 0:
                    self.save_qa_data()
                    self.save_progress()
                    logging.info("Checkpoint reached: %d files processed.", count)
                    print(f"Checkpoint saved: {count} files processed. Waiting to avoid timeout.")
                    time.sleep(30)

        # Final save
        self.save_qa_data()
        self.save_progress()
        logging.info("Final save complete. Processed %d new files.", count)
        print(f"Final save complete. Processed {count} new files.")

# Initialize the processor and start processing
if __name__ == "__main__":
    processor = QAProcessor(
        api_key=os.getenv('GEMINI_API2'),
        output_json="golden_dataset_generation/qa_output2.json",
        output_csv="golden_dataset_generation/qa_output2.csv",
        folder_paths=["golden_dataset_generation/data2"]
    )
    processor.process_folders()