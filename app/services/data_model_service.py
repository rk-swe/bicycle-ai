import json

import pandas as pd
from pydantic import BaseModel
from pydantic_ai import Agent

from app import database
from app.schemas.db_schemas import DatabaseSchema, TableSchema
from app.schemas.file_schemas import InputFile


def create_model_and_store_data(
    input_file: InputFile, df: pd.DataFrame
) -> tuple[pd.DataFrame, TableSchema]:
    print("create_model_and_store_data")

    table_schema = create_table_schema(input_file, df)

    try:
        for column in table_schema.columns:
            if column.data_type == "TIMESTAMP":
                df[column] = pd.to_datetime(df[column])
    except Exception:
        pass

    with database.engine.connect() as conn:
        df.to_sql(
            input_file.sql_table_name,
            con=conn,
            if_exists="replace",
            index=False,
            chunksize=100,
        )

    print("success")
    return df, table_schema


####


class TableSchemaAgentDeps(BaseModel):
    table_name: str
    columns: list[str]
    column_dtypes: dict[str, str]
    column_value_counts_head: dict[str, dict]
    column_unique_counts: dict[str, int]
    rows: list[dict]


table_schema_agent = Agent(
    "openai:gpt-4o",
    # deps_type=TableSchemaAgentDeps,
    output_type=TableSchema,
    instructions=(
        """
        You are an assistant that creates a single TableSchema JSON object (matching the TableSchema Pydantic model). Follow these rules exactly:

        1. USE ONLY the data in (`table_name`, `columns`, `column_dtypes`, `column_value_counts_head`, `column_unique_counts`, `rows`). Do NOT invent columns, tables, or values.
        2. Preserve column names exactly as they appear in `columns`.
        3. data_type: the column's PostgreSQL SQL type (e.g., `INTEGER`, `BIGINT`, `DOUBLE PRECISION`, `VARCHAR`, `BOOLEAN`, `TIMESTAMP`) based on `column_dtypes` and `rows`.
            - If the column_dtype is string/object and values are string keep the data type as `VARCHAR`.
        4. For each column, produce:
        - name: the exact column name.
        - description: 1-2 sentences about the column. If you cannot describe it confidently, write "No clear description from provided data."
        - possible_values:
            - See the column meaning and column values and if column is object/string and has low cardinality (column_unique_counts <= 5), list the possible values
            - Otherwise, set possible_values to null.
            - For boolean columns dont give possible values.
            - For integer columns dont give possible values.
        5. Heuristics:
        - datetime-like columns: describe as datetime, possible_values = null.
        - If all values are missing in deps: description = "No information available in provided data.", possible_values = null.
        6. Be conservative: never invent facts or columns. Base everything on deps.
        """
    ),
)


def create_table_schema(input_file: InputFile, df: pd.DataFrame) -> TableSchema:
    print("create_table_schema", input_file.sql_table_name)
    deps = TableSchemaAgentDeps(
        table_name=input_file.sql_table_name,
        columns=df.columns.tolist(),
        column_dtypes={
            c: str(x) for c, x in zip(df.columns.tolist(), df.dtypes.tolist())
        },
        column_value_counts_head={
            c: df[c].value_counts().head(10).to_dict() for c in df.columns
        },
        column_unique_counts={c: int(df[c].nunique(dropna=False)) for c in df.columns},
        rows=df.head(10).to_dict(orient="records"),
    )
    result = table_schema_agent.run_sync(
        deps.model_dump_json(),
        # deps=deps,
    )
    return result.output


def create_and_store_database_schema(
    input_files: list[InputFile], df_list: list[pd.DataFrame]
) -> None:
    table_schemas = [
        create_table_schema(input_file, df)
        for input_file, df in zip(input_files, df_list)
    ]
    store_database_schema(table_schemas)


def store_database_schema(table_schemas: list[TableSchema]) -> None:
    database_schema = DatabaseSchema(
        # name="",
        # description="",
        tables=[table_schemas],
    )
    with open("app/database_schema.json", "w") as fp:
        json.dump(database_schema.model_dump(), fp)


def get_database_schema() -> DatabaseSchema:
    with open("app/database_schema.json", "r") as fp:
        database_schema = json.load(fp)

    database_schema = DatabaseSchema.model_validate(database_schema)
    return database_schema
