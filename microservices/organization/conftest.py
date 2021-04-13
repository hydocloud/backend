import pytest
import uuid
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.organizations import Base, Organization


@pytest.fixture(scope="function")
def setup_database():

    engine = create_engine(
        "postgresql://postgres:ciaociao@localhost:5432/test_database"
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def setup_org_id(setup_database):

    org = Organization( 
        name = "asd",
        license_id = 1,
        owner_id=uuid.uuid4().__str__(),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    setup_database.add(org)
    setup_database.commit()
    setup_database.refresh(org)
    return org
