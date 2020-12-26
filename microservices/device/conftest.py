import pytest
import uuid
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.devices import Base, DeviceGroups


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
