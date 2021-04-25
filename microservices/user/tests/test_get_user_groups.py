import json
import sys

sys.path.append("./src/edit_user_groups")
from models.users import UserGroupsApiEditInput  # noqa: E402

from src.get_user_groups.get import get_user_groups  # noqa: E402


def test_get_user_group_with_id(setup_user_group, setup_user_group_belong, session):
    res = get_user_groups(
        connection=session,
        user_group_id=setup_user_group.id,
        owner_id=setup_user_group.owner_id,
    )
    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert body["data"][0]["name"] == "saeeqw"
    assert body["data"][0]["organizationId"] == 1


def test_get_user_groups(setup_user_group, setup_user_group_belong, session):
    res = get_user_groups(connection=session, owner_id=setup_user_group.owner_id)
    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert body["data"][0]["name"] == "saeeqw"
    assert body["data"][0]["organizationId"] == 1
