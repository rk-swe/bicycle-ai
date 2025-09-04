import os
from contextlib import contextmanager
from typing import Generator

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

DB_URL = os.environ["DB_URL"]
engine = sa.create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_ctx_mgr = contextmanager(get_db)
