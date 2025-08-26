import pandas as pd

from schemas.file_schemas import InputFile


def get_column_renamer(input_file: InputFile, df: pd.DataFrame) -> dict[str, str]:
    # TODO: implement function
    return {x: x for x in df.columns.tolist()}
