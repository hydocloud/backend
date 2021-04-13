import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.organizations import Base


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
