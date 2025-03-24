from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from rag_pipeline import chatbot
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas import EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_PGARG")

llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                api_key=gemini_api_key
            )
embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", 
                google_api_key=gemini_api_key
            )

dataset = []

rag = chatbot

for query,reference in zip(sample_queries,expected_responses):

    relevant_docs = rag.get_most_relevant_docs(query)
    response = rag.generate_answer(query, relevant_docs)
    dataset.append(
        {
            "user_input":query,
            "retrieved_contexts":relevant_docs,
            "response":response,
            "reference":reference
        }
    )

evaluation_dataset = EvaluationDataset.from_list(dataset)

evaluator_llm = LangchainLLMWrapper(llm)


result = evaluate(dataset=evaluation_dataset,metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],llm=evaluator_llm)
result