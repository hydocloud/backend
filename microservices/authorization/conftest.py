import sys

import boto3
import pytest
from faker import Faker
from moto import mock_dynamodb2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.append("../shared/")  # Add layer to path
sys.path.append("./models/")
from models.authorization import Authorization, Base
from models.devices import Base as Base_device

faker = Faker()


@pytest.fixture(scope="session")
def engine():
    return (
        create_engine("postgresql://postgres:ciaociao@localhost:5432/test_database"),
        create_engine("postgresql://postgres:ciaociao@localhost:5432/test_database"),
    )


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine[0])
    Base_device.metadata.create_all(engine[1])
    yield
    Base.metadata.drop_all(engine[0])
    Base_device.metadata.drop_all(engine[1])


@pytest.fixture
def authorizations_session(engine, tables):
    connection = engine[0].connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    session.commit()

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture
def devices_session(engine, tables):
    connection = engine[1].connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    session.commit()

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture
def populate_db(authorizations_session):
    authorizations = [
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_limit=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        ),
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_limit=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        ),
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_limit=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        ),
    ]
    authorizations_session.bulk_save_objects(authorizations, return_defaults=True)
    authorizations_session.commit()

    return authorizations


@mock_dynamodb2
@pytest.fixture(scope="function")
def dynamodb():
    """Mocked DynamoDB Fixture."""
    with mock_dynamodb2():
        dynamodb = boto3.resource("dynamodb", "eu-west-1")
        dynamodb.create_table(
            TableName="authorization_sessions",
            KeySchema=[
                {"AttributeName": "service_id", "KeyType": "HASH"},
                {"AttributeName": "message", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "service_id", "AttributeType": "S"},
                {"AttributeName": "message", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield dynamodb


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_NAME", "5432")
    monkeypatch.setenv("DB_ENGINE", "5432")
    monkeypatch.setenv("DB_USER", "5432")
    monkeypatch.setenv("DB_PASSWORD", "5432")
    monkeypatch.setenv("DB_INDY_PORT", "5432")
    monkeypatch.setenv("DB_INDY_HOST", "localhost")
    monkeypatch.setenv("DB_INDY_NAME", "5432")
    monkeypatch.setenv("DB_INDY_ENGINE", "5432")
    monkeypatch.setenv("DB_INDY_USER", "5432")
    monkeypatch.setenv("DB_INDY_PASSWORD", "5432")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")

