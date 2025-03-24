import csv
import time
from datetime import datetime
from bert_score import score
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from data.questions_list import context_questions
from rag_pipeline import chatbot

# Define log file paths
LOG_FILE = "logging/log_queries1.log"
LOG_FILE_CSV = "logging/log_queries1.csv"

def write_log(message, error=False):
    """Writes log messages with timestamps. Errors are marked separately."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_type = "ERROR" if error else "INFO"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp} - {log_type}: {message}\n")

class ChatbotEvaluator:
    def __init__(self, log_file=LOG_FILE, log_file_csv=LOG_FILE_CSV):
        self.log_file = log_file
        self.log_file_csv = log_file_csv
    
    def get_response(self, question: str) -> str:
        """Fetches response from the chatbot and logs errors if any."""
        try:
            response = chatbot.ask_question(question)
            if 'answer' not in response:
                raise ValueError(f"Invalid response format: {response}")
            return response['answer']
        except Exception as e:
            write_log(f"Error getting response for question '{question}': {str(e)}", error=True)
            return "Error: Unable to retrieve response."

    def evaluate_response(self, generated_answer: str, actual_answer: str):
        """Evaluates the chatbot's response using BERTScore and logs errors."""
        try:
            P, R, F1 = score([generated_answer], [actual_answer], lang="en", rescale_with_baseline=True)
            return P.tolist()[0], R.tolist()[0], F1.tolist()[0]
        except Exception as e:
            write_log(f"Error evaluating response '{generated_answer}': {str(e)}", error=True)
            return 0.0, 0.0, 0.0  # Return zero scores to prevent crashing
    
    def log_interaction(self, question: str, actual_answer: str, generated_answer: str, P, R, F1,CS):
        """Logs the user query and response in both a text file and a CSV file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Log in text file
            with open(self.log_file, "a") as txt_file:
                txt_file.write(f"{timestamp}\nQ: {question}\nActual Answer: {actual_answer}\nA: {generated_answer}\nP: {P}\nR: {R}\nF1: {F1}\nCS: {CS}\n")

            # Log in CSV file
            with open(self.log_file_csv, "a", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([question, actual_answer, generated_answer, P, R, F1,CS])
        except Exception as e:
            write_log(f"Error logging interaction: {str(e)}", error=True)
    

    def calculate_cosine_similarity(self,sentence1, sentence2):
        """
        Calculates the cosine similarity between two sentences.

        Args:
            sentence1 (str): The first sentence.
            sentence2 (str): The second sentence.

        Returns:
            float: The cosine similarity score (between 0 and 1), or None if an error occurs.
        """
        try:
            sentences = [sentence1, sentence2]
            vectorizer = TfidfVectorizer()  # Use TF-IDF for text vectorization
            tfidf_matrix = vectorizer.fit_transform(sentences)  # Create TF-IDF matrix

            # Calculate cosine similarity
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity_score

        except Exception as e:
            print(f"An error occurred: {e}")
            return None






    def run_evaluation(self):
        """Runs the chatbot evaluation for all questions and logs errors if they occur."""
        try:
            for question_data in context_questions:
                try:
                    question = question_data.get('question', '').strip()
                    actual_answer = question_data.get('answer', '').strip()

                    if not question:
                        raise ValueError("Question is missing or empty.")

                    generated_answer = self.get_response(question)
                    time.sleep(6)  # Prevent rate limiting
                    
                    P, R, F1 = self.evaluate_response(generated_answer, actual_answer)

                    CS = self.calculate_cosine_similarity(generated_answer, actual_answer)
                    self.log_interaction(question, actual_answer, generated_answer, P, R, F1,CS)
                    
                    print(f"Evaluated: {question}")
                    write_log(f"Successfully evaluated: {question}")
                except Exception as e:
                    write_log(f"Error evaluating question '{question}': {str(e)}", error=True)
                with open(LOG_FILE, "a") as log_file:
                    log_file.write(f"{'-'*40}\n")
        except Exception as main_error:
            write_log(f"Unhandled error in run_evaluation: {str(main_error)}", error=True)
            raise main_error

if __name__ == "__main__":
    try:
        evaluator = ChatbotEvaluator()
        evaluator.run_evaluation()
    except Exception as main_error:
        write_log(f"Critical failure in main execution: {str(main_error)}", error=True)
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{'-'*40}\n")
        raise main_error
    
    
