import datetime
import sys
import uuid

import boto3
import pytest
from moto import mock_secretsmanager, mock_sqs

sys.path.append("../shared/")  # Add layer to path
sys.path.append("./models/")
from models.devices import Base, DeviceGroups  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


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
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture(scope="function")
def setup_device_group_id(session):

    device_groups = DeviceGroups(
        name="asd",
        organization_id=1,
        owner_id=uuid.uuid4().__str__(),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    session.add(device_groups)
    session.commit()
    session.refresh(device_groups)
    return device_groups.id


@mock_sqs
@pytest.fixture(scope="function")
def sqs_queue(monkeypatch):
    with mock_sqs():
        sqs = boto3.client("sqs", region_name="eu-west-1")
        queue_url = sqs.create_queue(QueueName="create-authorization-device")
        monkeypatch.setenv("QUEUE_URL", queue_url["QueueUrl"])
        yield sqs


@mock_secretsmanager
@pytest.fixture(scope="function")
def secret():
    with mock_secretsmanager():
        conn = boto3.client("secretsmanager", region_name="eu-west-1")
        conn.create_secret(
            Name="java-util-test-password",
            SecretString="ciaociaociaociaociaociaociaociao",
        )
        yield conn
