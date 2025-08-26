import pandas as pd
from openai import OpenAI
from services import utils

from app.schemas.file_schemas import InputFile

client = OpenAI()


# NOTE: retry once if error
def get_column_renamer(input_file: InputFile, df: pd.DataFrame) -> dict[str, str]:
    user_prompt = f"""
        You are helping standardize column names for a table.

        Task:
        - Return a JSON object mapping each original column name to a better one.
        - Use snake_case.
        - Keep names concise but descriptive.
        - Do NOT add or remove columns, only rename.

        File Name: {input_file.file_name_with_ext}
        Suggested SQL table: {input_file.sql_table_name}

        Here are the dataframe columns and dtypes:
        {df.dtypes.to_dict()}
    """

    response = client.responses.parse(
        model="gpt-5",
        input=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        text_format=dict[str, str],
    )
    column_renamer = response.output_parsed

    # validate
    missing = set(df.columns) - set(column_renamer.keys())
    extra = set(column_renamer.keys()) - set(df.columns)
    if missing or extra:
        raise ValueError(f"Column mapping mismatch: missing={missing}, extra={extra}")

    # enforce snake_case
    column_renamer = {
        col: utils.to_snake_case(new) for col, new in column_renamer.items()
    }

    return column_renamer
