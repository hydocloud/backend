from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ


def init_db():

    db_host = environ["DB_HOST"]
    db_port = environ["DB_PORT"]
    db_name_authorizations = environ["DB_NAME_AUTHORIZATIONS"]
    db_user_authorizations = environ["DB_USER_AUTHORIZATIONS"]
    db_password_authorizations = environ["DB_PASSWORD_AUTHORIZATIONS"]
    db_name_devices = environ["DB_NAME_DEVICES"]
    db_user_devices = environ["DB_USER_DEVICES"]
    db_password_devices = environ["DB_PASSWORD_DEVICES"]
    db_engine = environ["DB_ENGINE"]
    devices_database_uri = "{}://{}:{}@{}:{}/{}".format(
        db_engine,
        db_user_devices,
        db_password_devices,
        db_host,
        db_port,
        db_name_devices,
    )
    authorizations_database_uri = "{}://{}:{}@{}:{}/{}".format(
        db_engine,
        db_user_authorizations,
        db_password_authorizations,
        db_host,
        db_port,
        db_name_authorizations,
    )

    authorizations_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=create_engine(authorizations_database_uri),
    )
    devices_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=create_engine(devices_database_uri),
    )

    return authorizations_session(), devices_session()
