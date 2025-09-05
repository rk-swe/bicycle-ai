from enum import StrEnum

import pandas as pd
from openai import OpenAI
from pydantic import BaseModel

from app.schemas.file_schemas import InputFile

client = OpenAI()


class MissingValueMethod(StrEnum):
    fill_mean = "fill_mean"
    fill_median = "fill_median"
    fill_mode = "fill_mode"
    fill_linear_interpolation = "fill_linear_interpolation"
    ffill = "ffill"
    bfill = "bfill"
    fill_constant = "fill_constant"


class MissingValueStrategy(BaseModel):
    method: MissingValueMethod
    value: str | None


def make_table_context(input_file: InputFile, df: pd.DataFrame) -> dict:
    table_context = {
        "table_name": input_file.file_name,
        "table_column_dtypes": df.dtypes,
    }
    return table_context


def make_column_context(df: pd.DataFrame, column: str) -> dict:
    column_context = {
        "column_name": df[column].name,
        "dtype": str(df[column].dtype),
        "num_missing": int(df[column].isnull().sum()),
        "num_total": int(len(df[column])),
        "missing_ratio": float(df[column].isnull().mean()),
        "value_counts": df[column].value_counts().head(5).to_dict(),
        "describe": df[column].describe(include="all").to_dict(),
    }
    return column_context


def handle_missing_data(input_file: InputFile, df: pd.DataFrame) -> pd.DataFrame:
    table_context = make_table_context(input_file, df)

    for i, column in enumerate(df.columns):
        df = handle_one_column(df, i, column, table_context)

    return df


def handle_one_column(
    df: pd.DataFrame, enumerate_index: int, column: str, table_context
) -> pd.DataFrame:
    print(enumerate_index, len(df.columns), column)

    if not df[column].isnull().any():
        print("Skip, no missing values")
        return df

    if df[column].isnull().all():
        print("Skip, all values null")
        return df

    user_prompt = f"""
    You are deciding how to fill missing values in a DataFrame column.

    Table context:
    {table_context}

    Column context:
    {make_column_context(df, column)}

    Available methods:
    - fill_mean
    - fill_median
    - fill_mode
    - fill_linear_interpolation
    - ffill
    - bfill
    - fill_constant(value)

    Task:
    Choose the best missing value imputation method for this column.
    Respond in the required schema (MissingValueStrategy).
    Only fill_constant needs value
    Other methods give value as None

    """

    # Call LLM
    response = client.responses.parse(
        model="gpt-5-mini",
        input=user_prompt,
        text_format=MissingValueStrategy,
    )

    method = response.output_parsed.method
    value = response.output_parsed.value

    print(f"{method}, {value}")

    # Apply imputation
    if method == "fill_mean":
        df[column] = df[column].fillna(df[column].mean())
    elif method == "fill_median":
        df[column] = df[column].fillna(df[column].median())
    elif method == "fill_linear_interpolation":
        df[column] = df[column].interpolate(method="linear")
    elif method == "ffill":
        df[column] = df[column].fillna(method="ffill")
    elif method == "bfill":
        df[column] = df[column].fillna(method="bfill")
    elif method == "fill_constant":
        df[column] = df[column].fillna(value)
    elif method == "fill_mode":
        modes = df[column].mode()
        if len(modes) >= 0:
            df[column] = df[column].fillna(modes.iloc[0])
    else:
        # fallback
        print("fallback")
        pass

    return df
