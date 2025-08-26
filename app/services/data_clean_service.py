import pandas as pd

from app.schemas.file_schemas import InputFile
from app.services import column_rename_service


def clean_data(input_file: InputFile, df: pd.DataFrame) -> pd.DataFrame:
    column_renamer = column_rename_service.get_column_renamer(input_file, df)
    df = df.rename(columns=column_renamer)

    # TODO: handle missing values

    return df
