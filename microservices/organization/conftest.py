import pytest
import uuid
import datetime
import sys

sys.path.append("../shared/")  # Add layer to path
sys.path.append("./models/")
sys.path.append("./src/create_organization")
sys.path.append("./src/delete_organization")
sys.path.append("./src/edit_organization")
sys.path.append("./src/get_organizations")
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from models.organizations import Base, Organization  # noqa: E402


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
def setup_org_id(session):

    org = Organization(
        name="asd",
        license_id=1,
        owner_id=uuid.uuid4().__str__(),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


@pytest.fixture(scope="function")
def setup_organizations(session):
    owner_id = uuid.uuid4().__str__()
    org = Organization(
        name="asd",
        license_id=1,
        owner_id=owner_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    org2 = Organization(
        name="asd2",
        license_id=1,
        owner_id=owner_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    org3 = Organization(
        name="asd3",
        license_id=1,
        owner_id=owner_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    organizations = [org, org2, org3]
    session.bulk_save_objects(organizations, return_defaults=True)
    return organizations[0], organizations[1], organizations[2]
