from datetime import datetime

import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app import database
from app.schemas.db_schemas import DatabaseSchema
from app.services import data_model_service

####


class MainAgentDeps(BaseModel):
    database_schema: DatabaseSchema


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
)


@plan_agent.instructions
def get_plan_agent_instructions(ctx: RunContext[MainAgentDeps]) -> str:
    instructions = f"""
    The user will ask questions about a database
    You are an agent that thinks and creates a plan on how to answer it.
    You need to give about the general description on how to solve question
    and you break the question into sub questions.

    database_schema:
    {ctx.deps.database_schema.model_dump()}

    """
    return instructions


####


sql_agent = Agent(
    "openai:gpt-4o",
    deps_type=MainAgentDeps,
    output_type=str,
)


@sql_agent.instructions
def get_sql_agent_instructions(ctx: RunContext[MainAgentDeps]) -> str:
    instructions = f"""
    You are an agent that creates sql for the  input question based on the database schema
    You then execute the sql against the database and get results.

    database_schema:
    {ctx.deps.database_schema.model_dump()}

    """
    return instructions


@sql_agent.tool
def execute_sql(ctx: RunContext[MainAgentDeps], sql_query: str) -> str:
    with database.engine.connect() as conn:
        db_records = conn.execute(sa.text(sql_query)).all()
        db_records = [db_record._asdict() for db_record in db_records]
        db_records = jsonable_encoder(db_records)

    return db_records


####


class SummaryAgentDeps(BaseModel):
    database_schema: DatabaseSchema
    question: str
    plan: Plan


summary_agent = Agent(
    "openai:gpt-4o",
    deps_type=SummaryAgentDeps,
    output_type=str,
)


@summary_agent.instructions
def get_summary_agent_instructions(ctx: RunContext[SummaryAgentDeps]) -> str:
    instructions = f"""
        You are an agent that takes database_schema, user question, and the plan and the plan_results 
        and answers the user in a correct way.

    database_schema:
    {ctx.deps.database_schema.model_dump()}

    question:
    {ctx.deps.question}

    plan:
    {ctx.deps.plan.model_dump()}

    """
    return instructions


####


main_agent = Agent(
    "openai:gpt-4o",
    deps_type=MainAgentDeps,
    output_type=str,
)


@main_agent.instructions
def get_main_agent_instructions(ctx: RunContext[MainAgentDeps]) -> str:
    instructions = f"""
    You are a agent that answers questions to for the user a user based on a database schema.
    You can create_plan for the user question.
    Then for each plan_item 
        you can use create_sql_and_execute.
    Then use summarise_plan_results to get an answer

    database_schema:
    {ctx.deps.database_schema.model_dump()}

    """
    return instructions


@main_agent.tool
def create_plan(ctx: RunContext[MainAgentDeps], question: str) -> Plan:
    print(f"main_agent, create_plan, {question}\n")

    plan_result = plan_agent.run_sync(
        question, deps=ctx.deps, message_history=message_history
    )

    print(f"main_agent, create_plan, {plan_result.output}\n\n")
    return plan_result.output


@main_agent.tool
def create_sql_and_execute(ctx: RunContext[MainAgentDeps], plan_item: PlanItem) -> str:
    print(f"main_agent, create_sql_and_execute, {plan_item}")

    sql_result = sql_agent.run_sync(
        plan_item.description, deps=ctx.deps, message_history=message_history
    )

    print(f"main_agent, create_sql_and_execute, {sql_result.output}")
    return sql_result.output


@main_agent.tool
def summarise_plan_results(
    ctx: RunContext[MainAgentDeps],
    question: str,
    plan: list[Plan],
    plan_results: list[str],
) -> str:
    print(f"main_agent, summarise_plan_results")
    print(f"question: {question}")
    print(f"plan: {plan}")
    print(f"plan_results: {plan_results}")

    deps = SummaryAgentDeps(
        database_schema=ctx.deps.database_schema,
        question=question,
        plan=plan,
    )
    summary_result = summary_agent.run_sync(
        str(plan_results), deps=deps, message_history=message_history
    )

    print(f"main_agent, summarise_plan_results, {summary_result.output}")
    return summary_result.output


####


message_history = []


def get_contextual_question(question: str) -> str:
    question = f"""
    Current datetime is {datetime.now().isoformat()}.
    Use this when interpreting relative time expressions like 'yesterday', 'this month', etc.
    
    Question: {question}
    """
    return question


def get_answer_workflow(question: str) -> str:
    question = get_contextual_question(question)

    database_schema = data_model_service.get_database_schema()

    main_agent_deps = MainAgentDeps(database_schema=database_schema)

    plan_result = plan_agent.run_sync(
        question, deps=main_agent_deps, message_history=message_history
    )
    plan = plan_result.output
    print(plan)
    # message_history.append(plan_result.new_messages())

    sql_results = []
    for plan_item in plan.items:
        sql_result = sql_agent.run_sync(
            plan_item.model_dump_json(),
            deps=main_agent_deps,
            message_history=message_history,
        )
        sql_results.append(sql_result)

    plan_results = [x.output for x in sql_results]
    print(plan_results)

    # for x in sql_results:
    #     message_history.append(x.new_messages())

    summary_agent_deps = SummaryAgentDeps(
        database_schema=database_schema,
        question=question,
        plan=plan,
    )
    summary_result = summary_agent.run_sync(
        plan_results, deps=summary_agent_deps, message_history=message_history
    )
    answer = summary_result.output
    print(answer)
    return answer


def get_answer_react(question: str) -> str:
    database_schema = data_model_service.get_database_schema()

    main_agent_deps = MainAgentDeps(database_schema=database_schema)

    result = main_agent.run_sync(
        question, deps=main_agent_deps, message_history=message_history
    )
    answer = result.output

    return answer


####


get_answer = get_answer_workflow
# get_answer = get_answer_react


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
        print(f"Question: {question}\n\n")
        print(f"Answer: {get_answer(question)}\n\n")
        print(f"{'-' * 50}\n\n")


def conversation_loop():
    while True:
        question = input("Question: ")
        print(f"\nAnswer: {get_answer(question)}\n\n")
        print(f"{'-' * 50}\n\n")


####
