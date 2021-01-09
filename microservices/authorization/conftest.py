import pytest
import boto3
from faker import Faker
from moto import mock_dynamodb2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.authorization import Base, Authorization

faker = Faker()


@pytest.fixture(scope="session")
def engine():
    return create_engine("postgresql://postgres:ciaociao@localhost:5432/test_database")


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    # transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    authorizations = [
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_time=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        ),
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_time=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        ),
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_time=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        )
    ]

    session.bulk_save_objects(authorizations)
    session.commit()

    yield session

    session.close()
    # roll back the broader transaction
    # transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture
def populate_db(session):
    authorizations = [
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_time=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        ),
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_time=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        ),
        Authorization(
            user_id=faker.uuid4(),
            device_id=faker.random_int(),
            access_time=faker.random_int(),
            start_time=faker.iso8601(),
            end_time=faker.iso8601(),
            created_at=faker.iso8601(),
            updated_at=faker.iso8601(),
        )
    ]
    session.bulk_save_objects(authorizations)
    session.commit()

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