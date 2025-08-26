import pandas as pd

from schemas.file_schemas import InputFile
from services import column_rename_service


def clean_and_store_data():
    input_files = [
        InputFile(folder_name="data", file_name="Airline ID to Name", file_ext="csv"),
        InputFile(folder_name="data", file_name="Flight Bookings", file_ext="csv"),
    ]

    for input_file in input_files:
        df = pd.read_csv(input_file.file_path)

        column_renamer = column_rename_service.get_column_renamer(input_file, df)
        df = df.rename(columns=column_renamer)

        # TODO: handle missing values

        # make schema

        # validate schema

        # create schema

        # insert data


def main():
    pass


if __name__ == "__main__":
    main()
