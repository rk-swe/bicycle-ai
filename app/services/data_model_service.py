import pandas as pd

from app import database
from app.schemas.file_schemas import InputFile


def create_model_and_store_data(input_file: InputFile, df: pd.DataFrame) -> None:
    # TODO: make schema, validate schema, create schema, insert data

    with database.engine.connect() as conn:
        df.to_sql(
            input_file.sql_table_name,
            con=conn,
            if_exists="replace",
            index=False,
            chunksize=100,
        )
