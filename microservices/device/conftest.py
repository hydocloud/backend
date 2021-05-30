import datetime
import sys
import uuid
import json
import boto3
import pytest
from moto import mock_secretsmanager, mock_sqs

sys.path.append("../shared/")  # Add layer to path
sys.path.append("./models/")
from models.devices import Base, DeviceGroups  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


ASYMMETRIC_KEYS = {
    "publicKey": "3059301306072a8648ce3d020106082a8648ce3d030107034200041e077a3600ebf9492aa024540d4f5301c6c4eb6c7d8463ffe15ce40d04e0a7be15073b42797c7c18ae00a9915fc5c02c6c8a1e5c007e096065d0cb353fd35e62",
    "privateKey": "308187020100301306072a8648ce3d020106082a8648ce3d030107046d306b02010104208188efb1d5413d79242e84f14b263b9162dd52a8bd3f3d29604c5da3de412f18a144034200041e077a3600ebf9492aa024540d4f5301c6c4eb6c7d8463ffe15ce40d04e0a7be15073b42797c7c18ae00a9915fc5c02c6c8a1e5c007e096065d0cb353fd35e62",
}


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
        conn.create_secret(
            Name="asymmetric-secret",
            SecretString=json.dumps(ASYMMETRIC_KEYS),
        )
        yield conn
