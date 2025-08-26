import pandas as pd
from openai import OpenAI
from pydantic import BaseModel

from app.schemas.file_schemas import InputFile
from app.services import utils

client = OpenAI()


class ColumnRenameField(BaseModel):
    old_name: str
    new_name: str


class ColumnRenameList(BaseModel):
    columns: list[ColumnRenameField]


# NOTE: retry once if error
def get_column_renamer(input_file: InputFile, df: pd.DataFrame) -> dict[str, str]:
    print("get_column_renamer")

    user_prompt = f"""
        You are helping standardize column names for a table.

        Your task:
        - Is to return a mapping from original column name to its new name.
        - Every original column must have a corresponding renamed column (no omissions).
        - Do not invent or remove columns.
        - Apply these rules when renaming:
            1. Correct spelling mistakes.
            2. Give full forms for short hand names
            3. Use snake_case format (all lowercase, underscores between words).
            4. Keep names concise but descriptive.
            5. Dont change name if it already makes sense

        Context:
        - File name: {input_file.file_name_with_ext}
        - Suggested SQL table: {input_file.sql_table_name}

        Dataframe columns with dtypes:
        {df.dtypes.to_dict()}
    """

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        text_format=ColumnRenameList,
    )
    column_renamer = {x.old_name: x.new_name for x in response.output_parsed.columns}

    # validate
    missing = set(df.columns) - set(column_renamer.keys())
    extra = set(column_renamer.keys()) - set(df.columns)
    if missing or extra:
        raise ValueError(f"Column mapping mismatch: missing={missing}, extra={extra}")

    # enforce snake_case
    column_renamer = {
        col: utils.to_snake_case(new) for col, new in column_renamer.items()
    }

    print(column_renamer)
    return column_renamer
