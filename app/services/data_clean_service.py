import pandas as pd

from app.schemas.file_schemas import InputFile
from app.services import column_rename_service, missing_data_service


def clean_data(input_file: InputFile, df: pd.DataFrame) -> pd.DataFrame:
    print("clean_data")
    print(df)

    column_renamer = column_rename_service.get_column_renamer(input_file, df)
    df = df.rename(columns=column_renamer)

    df = missing_data_service.handle_missing_data(input_file, df)

    print(df)
    return df
