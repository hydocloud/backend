""" Entry point lambda"""

import logging
from aws_lambda_powertools import Tracer
from get import get_organization, get_organizations

tracer = Tracer(service="get_organization")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    """
    Based on both path parameters or query parameters chose if
    user require info about one organization or multiple
    """

    owner_id = "e12c1545-1362-4162-9c3b-ebe2e20f2e57"

    if (
        "pathParameters" in event
        and event["pathParameters"] is not None
        and "id" in event["pathParameters"]
    ):
        organization_id = event["pathParameters"]["id"]
        response = get_organization(owner_id, organization_id)
    elif (
        "queryStringParameters" in event and event["queryStringParameters"] is not None
    ):

        if (
            "pageSize" in event["queryStringParameters"]
            and "page" in event["queryStringParameters"]
        ):
            page_number = event["queryStringParameters"]["page"]
            page_size = event["queryStringParameters"]["pageSize"]
            response = get_organizations(owner_id, int(page_number), int(page_size))
        elif "pageSize" in event["queryStringParameters"]:
            page_size = event["queryStringParameters"]["pageSize"]
            response = get_organizations(owner_id, page_size=int(page_size))
        elif "page" in event["queryStringParameters"]:
            page_number = event["queryStringParameters"]["page"]
            response = get_organizations(owner_id, page_number=int(page_number))
    else:
        response = get_organizations(owner_id)

    return {"statusCode": response.statusCode, "body": response.body.json()}