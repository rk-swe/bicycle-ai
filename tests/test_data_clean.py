import pandas as pd

from app.schemas.file_schemas import InputFile
from app.services import column_rename_service, missing_data_service


def test_get_column_renamer() -> None:
    input_file = InputFile(
        folder_name="data", file_name="Flight Bookings", file_ext="csv"
    )
    df = pd.read_csv(input_file.file_path)

    column_rename_service.get_column_renamer(input_file, df)


def test_handle_missing_data() -> None:
    input_file = InputFile(
        folder_name="data", file_name="test_missing_data", file_ext="csv"
    )
    df = pd.read_csv(input_file.file_path)

    missing_data_service.handle_missing_data(input_file, df)
