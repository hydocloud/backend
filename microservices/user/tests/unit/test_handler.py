import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest_postgresql import factories
from models.users import Base, UserGroups, UserGroupsApiInput
from create_user_groups.create import create_user_groups
from delete_user_groups.delete import delete_user_groups


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


def test_database(setup_database):

    # Gets the session from the fixture
    session = setup_database
    owner_id = "ff1af476-cf84-47e9-a25a-e109060d4006"

    ## Right behavior
    res = create_user_groups(
        owner_id=owner_id,
        payload=UserGroupsApiInput.parse_obj({"name": "test1", "organizationId": 1}),
        connection=session,
    )
    user_group_1_id = res.body["data"]["userGroups"][0]["id"]

    assert res.statusCode == 201
    assert res.body["data"]["userGroups"][0]["name"] == "test1"
    assert res.body["data"]["userGroups"][0]["organizationId"] == 1

    res = delete_user_groups(
        owner_id=owner_id, connection=session, user_group_id=user_group_1_id
    )
    assert res.statusCode == 201
    assert res.body["message"] == "Ok"

    # Bad behavior

    res = delete_user_groups(
        owner_id=owner_id, connection=session, user_group_id=100000
    )
    assert res.statusCode == 404
    assert res.body["message"] == "Not found"

    res = delete_user_groups(
        owner_id="asdsads", connection=session, user_group_id=user_group_1_id
    )
    assert res.statusCode == 500
    assert res.body["message"] == "Internal server error"
