import pytest
import json
from create_organization.create import create_organization

OWNER_ID = "ff1af476-cf84-47e9-a25a-e109060d4006"


@pytest.fixture
def device() -> dict:
    return {
        "name": "test",
        "licenseId": 1,
    }


def test_create_ok(device, setup_database):
    res = create_organization(
        owner_id=OWNER_ID, payload=device, connection=setup_database
    )
    print(res)
    body = json.loads(res.body)
    assert res.statusCode == 201
    assert body["data"]["licenseId"] == device["licenseId"]
    assert body["data"]["ownerId"] == OWNER_ID
    assert body["data"]["name"] == device["name"]


def test_create_ok(device, setup_database):
    del device["licenseId"]
    res = create_organization(
        owner_id=OWNER_ID, payload=device, connection=setup_database
    )
    assert res["statusCode"] == 400
