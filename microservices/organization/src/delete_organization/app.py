import logging
from delete import delete_organization
from database import init_db
from aws_lambda_powertools import Tracer  # type: ignore

tracer = Tracer(service="delete_organization")

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
    response = delete_organization(
        owner_id=owner_id, organization_id=organization_id, connection=CONNECTION
    )

    return {"statusCode": response.statusCode, "body": response.body.json()}
