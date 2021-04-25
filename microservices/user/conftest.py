import datetime
import sys
import uuid

import boto3
import pytest

sys.path.append("../shared/")  # Add layer to path
sys.path.append("./models/")
from models.users import Base, UserGroups, UserBelongUserGroups  # noqa: E402
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
def setup_user_group(session):

    user_group = UserGroups(
        name="asd",
        organization_id=1,
        owner_id=uuid.uuid4().__str__(),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )

    session.add(user_group)
    session.commit()
    session.refresh(user_group)
    return user_group


@pytest.fixture(scope="function")
def setup_user_group_belong(session, setup_user_group):

    user_group_belong = UserBelongUserGroups(
        user_id=uuid.uuid4().__str__(),
        user_group_id=setup_user_group.id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )

    session.add(user_group_belong)
    session.commit()
    session.refresh(user_group_belong)
    return user_group_belong
