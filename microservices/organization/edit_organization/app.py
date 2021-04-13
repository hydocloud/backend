import logging
import json
from edit import edit_organization
from models.organizations import OrganizationsUpdate
from database import init_db
from aws_lambda_powertools import Tracer  # type: ignore

tracer = Tracer(service="edit_organization")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

CONNECTION = None


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    global CONNECTION

    if CONNECTION is None:
        CONNECTION = init_db()

    owner_id = event["requestContext"]["authorizer"]["lambda"]["sub"]
    organization_id = event["pathParameters"]["id"]
    payload = json.loads(event["body"])
    OrganizationsUpdate.parse_obj(payload)
    response = edit_organization(owner_id, organization_id, payload, CONNECTION)

    return response
