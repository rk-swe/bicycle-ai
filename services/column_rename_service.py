import pandas as pd

from schemas.file_schemas import InputFile


def get_column_renamer(input_file: InputFile, df: pd.DataFrame) -> dict[str, str]:
    # TODO: implement function

    # make the prompt
    # call llm
    # get response
    # validate it
    # if error retry once
    # return result

    return {x: x for x in df.columns.tolist()}
