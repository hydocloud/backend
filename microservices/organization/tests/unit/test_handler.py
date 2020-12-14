import pytest
import boto3
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from get_organizations.get import get_organization, get_organizations
from create_organization.create import create_organization, create_user_group
import create_organization.create as create
from edit_organization.edit import edit_organization
from delete_organization.delete import delete_organization
from moto import mock_sqs


@mock_sqs
def test_sqs_send_message():
    sqs = boto3.client('sqs', region_name='eu-west-1')
    queue = sqs.create_queue(QueueName='create-user-group')
    expected_message = json.dumps({"name": "DEFAULT", "organizationId": 1000, "ownerId": "asdasd"})
    create.QUEUE_URL = queue["QueueUrl"]
    create_user_group(organization_id=1000, owner_id="asdasd")
    sqs_messages = sqs.receive_message(QueueUrl=queue["QueueUrl"])
    assert sqs_messages["Messages"][0]["Body"] == expected_message
    assert len(sqs_messages["Messages"]) == 1


@pytest.fixture(scope='function')
def setup_database():

    engine = create_engine("postgresql://postgres:ciaociao@localhost:5432/test_database")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_database(setup_database):

    # Gets the session from the fixture
    session = setup_database
    owner_id = "ff1af476-cf84-47e9-a25a-e109060d4006"

    res = create_organization(owner_id=owner_id, payload={"name": "test1", "licenseId": 1}, connection=session)
    org_1_id = res.body.data.organizations[0].id
    assert res.statusCode == 201
    assert res.body.data.organizations[0].name == "test1"
    assert res.body.data.organizations[0].licenseId == 1 

    res = get_organization(owner_id=owner_id, connection=session, organization_id=org_1_id)
    assert res.statusCode == 201
    assert res.body.data.organizations[0].name == "test1"
    assert res.body.data.organizations[0].licenseId == 1
    assert res.body.data.organizations[0].id == org_1_id

    res = edit_organization(owner_id=owner_id, organization_id=org_1_id, payload={"name": "edit", "licenseId": 2}, connection=session)
    org_1_id = res.body.data.organizations[0].id
    assert res.statusCode == 201
    assert res.body.data.organizations[0].name == "edit"
    assert res.body.data.organizations[0].licenseId == 2

    res = get_organization(owner_id=owner_id, connection=session, organization_id=org_1_id)
    assert res.statusCode == 201
    assert res.body.data.organizations[0].name == "edit"
    assert res.body.data.organizations[0].licenseId == 2
    assert res.body.data.organizations[0].id == org_1_id

    res = delete_organization(owner_id=owner_id, connection=session, organization_id=org_1_id)
    assert res.statusCode == 201
    assert res.body.message == "ok"

    # Test dataset
    dataset_size = 30
    page_size = 10
    page_number = 2
    org_ids = []

    for i in range(dataset_size):
        tmp = create_organization(owner_id=owner_id, payload={"name": "test1", "licenseId": 1}, connection=session)
        org_ids.append(tmp.body.data.organizations[0].id)

    res = get_organizations(owner_id=owner_id, connection=session)
    assert res.statusCode == 201
    assert res.body.data.total == dataset_size

    res = get_organizations(owner_id=owner_id, page_size=10, connection=session)
    assert res.statusCode == 201
    assert res.body.data.total == dataset_size
    assert res.body.data.totalPages == dataset_size/page_size

    res = get_organizations(owner_id=owner_id, page_size=page_size, page_number=page_number, connection=session)
    assert res.body.data.nextPage == page_number + 1
    assert res.body.data.previousPage == page_number - 1

    res = get_organizations(owner_id=owner_id, page_size=page_size, page_number=dataset_size/page_size, connection=session)
    assert res.body.data.nextPage is None
    assert res.body.data.previousPage == page_number

    res = get_organizations(owner_id=owner_id, page_size=page_size, page_number=1, connection=session)
    assert res.body.data.nextPage == page_number
    assert res.body.data.previousPage is None
        
    for i in range(dataset_size):
        delete_organization(owner_id=owner_id, connection=session, organization_id=org_ids[i])
