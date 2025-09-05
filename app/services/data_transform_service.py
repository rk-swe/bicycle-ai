import pandas as pd

from app.schemas.file_schemas import InputFile
from app.services import data_clean_service, data_model_service


def transform_data():
    input_files = [
        InputFile(folder_name="data", file_name="Airline ID to Name", file_ext="csv"),
        InputFile(folder_name="data", file_name="Flight Bookings", file_ext="csv"),
    ]

    df_list = []
    table_schema_list = []
    for index, input_file in enumerate(input_files):
        print(f"{index+1}/{len(input_files)} {input_file.file_path}")

        df = pd.read_csv(input_file.file_path)

        df = data_clean_service.clean_data(input_file, df)

        df, table_schema = data_model_service.create_model_and_store_data(
            input_file, df
        )

        df_list.append(df)
        table_schema_list.append(table_schema)

    data_model_service.store_database_schema(table_schema_list)
    print("success")
