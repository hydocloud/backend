import logging
import json
from get import get_organization, get_organizations
from aws_lambda_powertools import Tracer

tracer = Tracer(service="get_organization")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):

    owner_id = "e12c1545-1362-4162-9c3b-ebe2e20f2e57"

    if event["pathParameters"] is not None and "id" in event["pathParameters"]:
        organization_id = event["pathParameters"]["id"]
        response = get_organization(owner_id, organization_id)
    elif (
        event["queryStringParameters"] is not None
        and "page" in event["queryStringParameters"]
    ):
        page_number = event["queryStringParameters"]["page"]
        response = get_organizations(owner_id, page_number)
    else:
        response = get_organizations(owner_id)

    return {"statusCode": response.statusCode, "body": response.body.json()}
