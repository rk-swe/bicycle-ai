from llama_index.core import ServiceContext, SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.openai import OpenAI

from app import database

sql_db = SQLDatabase(database.engine)

llm = OpenAI(model="gpt-4o-mini")

query_engine = NLSQLTableQueryEngine(sql_database=sql_db, llm=llm)


def get_answer(question: str) -> str:
    return query_engine.query(question)


def test_qa():
    questions = [
        # easy
        "Which airline has the most flights listed?",
        "What are the top three most frequented destinations?",
        "Number of bookings for American Airlines yesterday.",
        # medium
        "Average flight delay per airline.",
        "Month with the highest number of bookings.",
        # hard
        "Patterns in booking cancellations, focusing on specific days or airlines with high cancellation rates.",
        "Analyze seat occupancy to find the most and least popular flights.",
    ]
    for question in questions:
        print(f"Question: {question}")
        print(f"Answer: {get_answer(question)}")
        print("-" * 50)


def conversation_loop():
    while True:
        question = input("Question: ")
        print(f"Answer: {get_answer(question)}")
        print("-" * 50)
