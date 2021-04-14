import pytest
import json
from delete_organization.delete import delete_organization


def test_delete_ok(session, setup_org_id):
    res = delete_organization(
        owner_id=setup_org_id.owner_id,
        organization_id=setup_org_id.id,
        connection=session,
    )
    assert res.statusCode == 201


def test_delete_not_found(session, setup_org_id):
    res = delete_organization(
        owner_id=setup_org_id.owner_id,
        organization_id=10000,
        connection=session,
    )
    assert res.statusCode == 404
