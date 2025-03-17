import csv
import time
from data.questions_list import context_questions
from rag_pipeline import chatbot
from bert_score import score

class ChatbotEvaluator:
    def __init__(self, log_file_txt="logging/log_queries.txt", log_file_csv="logging/log_queries.csv"):
        self.log_file_txt = log_file_txt
        self.log_file_csv = log_file_csv
    
    def get_response(self, question: str) -> str:
        """Fetches response from the chatbot."""
        return chatbot.ask_question(question)['answer']
    
    def evaluate_response(self, generated_answer: str, actual_answer: str):
        """Evaluates the chatbot's response using BERTScore."""
        P, R, F1 = score([generated_answer], [actual_answer], lang="en", rescale_with_baseline=True)
        return P.tolist()[0], R.tolist()[0], F1.tolist()[0]
    
    def log_interaction(self, question: str, actual_answer: str, generated_answer: str, P, R, F1):
        """Logs the user query and response in both a text file and a CSV file."""
        with open(self.log_file_txt, "a") as txt_file:
            txt_file.write(f"Q: {question}\nActual answer: {actual_answer}\nA: {generated_answer}\nP: {P}\nR: {R}\nF1: {F1}\n{'-'*40}\n")
        
        with open(self.log_file_csv, "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([question, actual_answer, generated_answer, P, R, F1])
    
    def run_evaluation(self):
        """Runs the chatbot evaluation for all questions."""
        for question_data in context_questions:
            question = question_data['question']
            actual_answer = question_data['answer']
            generated_answer = self.get_response(question)
            time.sleep(6)  # Prevent rate limiting
            
            P, R, F1 = self.evaluate_response(generated_answer, actual_answer)
            self.log_interaction(question, actual_answer, generated_answer, P, R, F1)
            print(f"Evaluated: {question}")

if __name__ == "__main__":
    evaluator = ChatbotEvaluator()
    evaluator.run_evaluation()
