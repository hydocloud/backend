import pytest
import json
from edit_organization.edit import edit_organization


def test_edit_ok(session, setup_org_id):
    res = edit_organization(
        owner_id=setup_org_id.owner_id,
        organization_id=setup_org_id.id,
        payload={"name": "edit", "licenseId": 2},
        connection=session,
    )
    body = json.loads(res.body)
    assert res.statusCode == 201
    assert body["data"]["licenseId"] == 2
    assert body["data"]["name"] == "edit"


def test_edit_no_org(session, setup_org_id):
    res = edit_organization(
        owner_id=setup_org_id.owner_id,
        organization_id=100000,
        payload={"name": "edit", "licenseId": 2},
        connection=session,
    )
    assert res["statusCode"] == 403
