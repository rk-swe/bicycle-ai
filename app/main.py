import pandas as pd

import app.database as database
from app.schemas.file_schemas import InputFile
from app.services import data_clean_service, data_model_service


def main():
    input_files = [
        InputFile(folder_name="data", file_name="Airline ID to Name", file_ext="csv"),
        InputFile(folder_name="data", file_name="Flight Bookings", file_ext="csv"),
    ]

    for input_file in input_files:
        df = pd.read_csv(input_file.file_path)

        df = data_clean_service.clean_data(input_file, df)

        data_model_service.create_model_and_store_data(input_file, df)


if __name__ == "__main__":
    main()
