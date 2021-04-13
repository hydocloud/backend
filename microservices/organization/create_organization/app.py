import logging
import json
from create import create_organization
from models.organizations import OrganizationBase
from database import init_db
from aws_lambda_powertools import Tracer  # type: ignore


tracer = Tracer(service="create_organization")

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
    payload = json.loads(event["body"])
    OrganizationBase.parse_obj(payload)
    response = create_organization(owner_id, payload, CONNECTION)

    return response
