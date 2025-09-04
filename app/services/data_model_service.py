import json

import pandas as pd

from app import database
from app.schemas.db_schemas import DatabaseSchema
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


def create_database_schema(input_file: InputFile, df: pd.DataFrame) -> None:
    database_schema = DatabaseSchema(name="", description="", tables=[])

    with open("app/database_schemas.json", "w") as fp:
        json.dump(database_schema.model_dump(), fp)


def get_database_schema() -> DatabaseSchema:
    with open("app/database_schemas.json", "r") as fp:
        database_schema = json.load(fp)

    database_schema = DatabaseSchema.model_validate(database_schema)
    return database_schema
