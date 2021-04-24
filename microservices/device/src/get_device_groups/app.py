""" Entry point lambda"""

import logging

from aws_lambda_powertools import Tracer
from database import init_db
from get_groups import get_device_groups

tracer = Tracer(service="get_device_groups")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
CONNECTION = None


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    """
    Based on both path parameters or query parameters chose if
    device require info about one device group or multiple
    """
    global CONNECTION
    owner_id = event["requestContext"]["authorizer"]["lambda"]["sub"]

    if CONNECTION is None:
        CONNECTION = init_db()

    if (
        "pathParameters" in event
        and event["pathParameters"] is not None
        and "id" in event["pathParameters"]
    ):
        device_group_id = event["pathParameters"]["id"]
        response = get_device_groups(
            connection=CONNECTION, owner_id=owner_id, device_group_id=device_group_id
        )
    elif (
        "queryStringParameters" in event and event["queryStringParameters"] is not None
    ):

        if (
            "pageSize" in event["queryStringParameters"]
            and "page" in event["queryStringParameters"]
        ):
            page_number = event["queryStringParameters"]["page"]
            page_size = event["queryStringParameters"]["pageSize"]
            response = get_device_groups(
                connection=CONNECTION,
                owner_id=owner_id,
                page_number=int(page_number),
                page_size=int(page_size),
            )
        elif "pageSize" in event["queryStringParameters"]:
            page_size = event["queryStringParameters"]["pageSize"]
            response = get_device_groups(
                connection=CONNECTION, owner_id=owner_id, page_size=int(page_size)
            )
        elif "page" in event["queryStringParameters"]:
            page_number = event["queryStringParameters"]["page"]
            response = get_device_groups(
                connection=CONNECTION, owner_id=owner_id, page_number=int(page_number)
            )
    else:
        response = get_device_groups(connection=CONNECTION, owner_id=owner_id)

    return response
