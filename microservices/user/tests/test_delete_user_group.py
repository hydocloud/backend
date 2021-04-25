import json
import sys

sys.path.append("./src/delete_user_groups")
from src.delete_user_groups.delete import delete_user_groups


def test_delete_group_ok(setup_user_group, session):
    res = delete_user_groups(
        owner_id=setup_user_group.owner_id,
        connection=session,
        user_group_id=setup_user_group.id,
    )
    body = json.loads(res["body"])
    assert res["statusCode"] == 201
    assert body["message"] == "Ok"


def test_delete_group_not_found(setup_user_group, session):

    res = delete_user_groups(
        owner_id=setup_user_group.owner_id, connection=session, user_group_id=100000
    )
    body = json.loads(res["body"])
    assert res["statusCode"] == 404
    assert body["message"] == "Not found"


def test_delete_group_ko(setup_user_group, session):
    res = delete_user_groups(
        owner_id="asdsads", connection=session, user_group_id=setup_user_group.id
    )
    body = json.loads(res["body"])
    assert res["statusCode"] == 500
    assert body["message"] == "Internal server error"
