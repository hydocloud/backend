import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest_postgresql import factories
from models.organizations import Base, Organization
from get_organizations.get import get_organization, get_organizations
from create_organization.create import create_organization
from edit_organization.edit import edit_organization
from delete_organization.delete import delete_organization

@pytest.fixture(scope='function')
def setup_database():

    engine = create_engine("postgresql://postgres:ciaociao@localhost:5432/test_database")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# @pytest.fixture(scope='function')
# def dataset(setup_database):
    
#     session = setup_database

#     # Creates user
#     org_1 = Organization(owner_id="ff1af476-cf84-47e9-a25a-e109060d4006", name="org1", license_id=1, created_at="2020-11-27 22:07:03", updated_at="2020-11-27 22:07:03" )
#     org_2 = Organization(owner_id="ff1af476-cf84-47e9-a25a-e109060d4006", name="org2", license_id=2, created_at="2020-11-27 22:07:03", updated_at="2020-11-27 22:07:03" )
#     session.add(org_1)
#     session.add(org_2)
#     session.commit()

#     yield session

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

    ### Test dataset
    dataset_size = 30
    page_size=10
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
    assert res.body.data.nextPage == None
    assert res.body.data.previousPage == page_number

    res = get_organizations(owner_id=owner_id, page_size=page_size, page_number=1, connection=session)
    assert res.body.data.nextPage == page_number
    assert res.body.data.previousPage == None
        

    for i in range(dataset_size):
        delete_organization(owner_id=owner_id, connection=session, organization_id=org_ids[i])
