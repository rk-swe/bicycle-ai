from dotenv import load_dotenv

load_dotenv()


from app.services import data_qa_service, data_transform_service


def main():
    # data_transform_service.transform_data()

    data_qa_service.test_qa()

    # data_qa_service.conversation_loop()


if __name__ == "__main__":
    main()
