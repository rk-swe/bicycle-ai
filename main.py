from dotenv import load_dotenv

load_dotenv()


from app.services import data_qa_basic, data_transform_service
from tests import test_data_clean


def main():
    # data_transform_service.transform_data()

    # data_qa_basic.test_qa()

    data_qa_basic.conversation_loop()

    # data_transform_service.test_handle_missing_data()

    pass


if __name__ == "__main__":
    main()
