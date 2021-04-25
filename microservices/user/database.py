from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def init_db() -> int:

    db_host = environ["DB_HOST"]
    db_port = environ["DB_PORT"]
    db_name = environ["DB_NAME"]
    db_user = environ["DB_USER"]
    db_password = environ["DB_PASSWORD"]
    db_engine = environ["DB_ENGINE"]
    database_uri = "{}://{}:{}@{}:{}/{}".format(
        db_engine, db_user, db_password, db_host, db_port, db_name
    )
    engine = create_engine(database_uri)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = Session()

    return db_session
