import json

import pandas as pd
from pydantic import BaseModel
from pydantic_ai import Agent

from app import database
from app.schemas.db_schemas import DatabaseSchema, TableSchema
from app.schemas.file_schemas import InputFile


def create_model_and_store_data(input_file: InputFile, df: pd.DataFrame) -> None:
    print("create_model_and_store_data")

    with database.engine.connect() as conn:
        df.to_sql(
            input_file.sql_table_name,
            con=conn,
            if_exists="replace",
            index=False,
            chunksize=100,
        )

    print("success")


####


class TableSchemaAgentDeps(BaseModel):
    table_name: str
    columns: list[str]
    column_dtypes: list[str]
    column_value_counts: dict[str, int]
    rows: list[dict]


table_schema_agent = Agent(
    "openai:gpt-4o",
    deps_type=TableSchemaAgentDeps,
    output_type=TableSchema,
    instructions=(
        """
        create a tables schema
        create good description for table and columns
        and add possible values to to columns if it is only limited to certain set of values
        """
    ),
)


def create_table_schema(input_file: InputFile, df: pd.DataFrame) -> TableSchema:
    deps = TableSchemaAgentDeps(
        table_name=input_file.sql_table_name,
        columns=df.columns.tolist(),
        column_dtypes={c: x for c, x in zip(df.columns.tolist(), df.dtypes.tolist())},
        column_value_counts={c: df[c].value_counts()[0:10] for c in df.columns},
        rows=df.head().to_dict(orient="records"),
    )
    result = table_schema_agent.run_sync("", deps=deps)
    return result.output


def create_and_store_database_schema(
    input_files: list[InputFile], df_list: list[pd.DataFrame]
) -> None:
    database_schema = DatabaseSchema(
        name="",
        description="",
        tables=[
            create_table_schema(input_file, df)
            for input_file, df in zip(input_files, df_list)
        ],
    )

    with open("app/database_schemas.json", "w") as fp:
        json.dump(database_schema.model_dump(), fp)


def get_database_schema() -> DatabaseSchema:
    with open("app/database_schemas.json", "r") as fp:
        database_schema = json.load(fp)

    database_schema = DatabaseSchema.model_validate(database_schema)
    return database_schema
