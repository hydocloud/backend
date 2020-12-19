import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.devices import (
    Base,
    DeviceGroupsApiInput,
)
from create_device_group.create import create_device_groups


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

    # Right behavior
    res = create_device_groups(
        owner_id=owner_id,
        payload=DeviceGroupsApiInput.parse_obj({"name": "test1", "organizationId": 1}),
        connection=session,
    )

    body = json.loads(res["body"])
    # device_group_1_id = body["data"]["deviceGroups"][0]["id"]
    assert res["statusCode"] == 201
    assert body["data"]["deviceGroups"][0]["name"] == "test1"
    assert body["data"]["deviceGroups"][0]["organizationId"] == 1

    # res = edit_device_group(
    #     owner_id=owner_id,
    #     device_group_id=device_group_1_id,
    #     payload=DeviceGroupsApiEditInput.parse_obj({"name": "saeeqw"}),
    #     connection=session,
    # )

    # body = json.loads(res["body"])
    # assert res["statusCode"] == 201
    # assert body["data"]["deviceGroups"][0]["name"] == "saeeqw"
    # assert body["data"]["deviceGroups"][0]["organizationId"] == 1

    # res = get_device_groups(connection=session, device_group_id=device_group_1_id, owner_id=owner_id)
    # body = json.loads(res["body"])
    # assert res["statusCode"] == 200
    # assert body["data"]["deviceGroups"][0]["name"] == "saeeqw"
    # assert body["data"]["deviceGroups"][0]["organizationId"] == 1

    # res = get_device_groups(connection=session, owner_id=owner_id)
    # body = json.loads(res["body"])
    # assert res["statusCode"] == 200
    # assert body["data"]["deviceGroups"][0]["name"] == "saeeqw"
    # assert body["data"]["deviceGroups"][0]["organizationId"] == 1

    # res = delete_device_groups(
    #     owner_id=owner_id, connection=session, device_group_id=device_group_1_id
    # )
    # body = json.loads(res["body"])
    # assert res["statusCode"] == 201
    # assert body["message"] == "Ok"

    # # Bad behavior

    # res = delete_device_groups(
    #     owner_id=owner_id, connection=session, device_group_id=100000
    # )
    # body = json.loads(res["body"])
    # assert res["statusCode"] == 404
    # assert body["message"] == "Not found"

    # res = delete_device_groups(
    #     owner_id="asdsads", connection=session, device_group_id=device_group_1_id
    # )
    # body = json.loads(res["body"])
    # assert res["statusCode"] == 500
    # assert body["message"] == "Internal server error"
