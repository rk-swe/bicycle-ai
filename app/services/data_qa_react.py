import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app import database

####


class MainAgentDeps(BaseModel):
    database_schema: str


main_agent = MainAgentDeps(
    "openai:gpt-4o",
    deps_type=MainAgentDeps,
    output_type=str,
    instructions=(
        """
        You are a agent that answers questions to a user based on a database schema.
        You can create_plan for the user question.
        Then for each plan_item 
            you can create_sql and then execute_sql.
            If there is any error in execute sql retry create_sql and execute_sql once.
        Then use summarise_results to get an answer for the user
        """
    ),
)


####


class PlanItem(BaseModel):
    index: int
    description: str


class Plan(BaseModel):
    description: str
    items: list[PlanItem]


plan_agent = Agent(
    "openai:gpt-4o",
    deps_type=MainAgentDeps,
    output_type=Plan,
    instructions=(
        """
        The user will ask questions about a database
        You are an agent that thinks and creates a plan on how to answer it.
        You need to give about the general description on how to solve question
        and you break the question into sub questions.
        """
    ),
)


####


sql_agent = Agent(
    "openai:gpt-4o",
    deps_type=MainAgentDeps,
    output_type=str,
    instructions=(
        """
        You are an agent that creates sql for the  input question based on the database schema
        """
    ),
)


@sql_agent.tool
def execute_sql(ctx: RunContext[MainAgentDeps], sql_query: str) -> str:
    with database.engine.connect() as conn:
        db_records = conn.execute(sa.text(sql_query)).all()
        db_records = jsonable_encoder(db_records)


####


class SummaryAgentDeps(BaseModel):
    database_schema: str
    question: str
    plan: Plan


summary_agent = Agent(
    "openai:gpt-4o",
    deps_type=SummaryAgentDeps,
    output_type=str,
    instructions=(
        """
        You are an agent that takes the user question, and the plan and the plan results 
        and answers the user in a correct way.
        """
    ),
)


####


message_history = []


def get_answer_workflow(question: str) -> str:
    main_agent_deps = MainAgentDeps(database_schema="")

    plan_result = plan_agent.run_sync(
        question, deps=main_agent_deps, message_history=message_history
    )
    plan = plan_result.output
    # message_history.append(plan_result.new_messages())

    sql_results = [
        sql_agent.run_sync(
            plan_item.model_dump_json(),
            deps=main_agent_deps,
            message_history=message_history,
        )
        for plan_item in plan.items
    ]
    # for x in sql_results:
    #     message_history.append(x.new_messages())

    plan_results = [x.output for x in sql_results]

    summary_result = summary_agent.run_sync(
        plan_result, message_history=message_history
    )


def get_answer_react(question: str) -> str:
    return ""


####


get_answer = get_answer_workflow


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
        print(f"Question: {question}", end="\n\n")
        print(f"Answer: {get_answer(question)}", end="\n\n")
        print("-" * 50, end="\n\n")


def conversation_loop():
    while True:
        question = input("Question: ")
        print(f"\nAnswer: {get_answer(question)}", end="\n\n")
        print("-" * 50, end="\n\n")


####
