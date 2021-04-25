import json
import sys

sys.path.append("./src/edit_user_groups")
from models.users import UserGroupsApiEditInput

from src.edit_user_group.edit import edit_user_group


def test_edit_group(setup_user_group, session):
    res = edit_user_group(
        owner_id=setup_user_group.owner_id,
        user_group_id=setup_user_group.id,
        payload=UserGroupsApiEditInput.parse_obj({"name": "saeeqw"}),
        connection=session,
    )

    body = json.loads(res["body"])
    assert res["statusCode"] == 201
    assert body["data"][0]["name"] == "saeeqw"
    assert body["data"][0]["organizationId"] == 1
