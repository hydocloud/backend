""" Entry point lambda"""

import logging
import json
from aws_lambda_powertools import Tracer
from get import get_user_groups
from database import init_db

tracer = Tracer(service="get_user_groups")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
CONNECTION = None


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    """
    Based on both path parameters or query parameters chose if
    user require info about one user group or multiple
    """
    global CONNECTION
    owner_id = "ddd6de86-52be-447b-a8e2-54f40fa78cd1"#event["requestContext"]["authorizer"]["lambda"]["sub"]

    if CONNECTION is None:
        CONNECTION = init_db()

    if (
        "pathParameters" in event
        and event["pathParameters"] is not None
        and "id" in event["pathParameters"]
    ):
        user_group_id = event["pathParameters"]["id"]
        response = get_user_groups(connection=CONNECTION, owner_id=owner_id, user_group_id=user_group_id)
    elif (
        "queryStringParameters" in event and event["queryStringParameters"] is not None
    ):

        if (
            "pageSize" in event["queryStringParameters"]
            and "page" in event["queryStringParameters"]
        ):
            page_number = event["queryStringParameters"]["page"]
            page_size = event["queryStringParameters"]["pageSize"]
            response = get_user_groups(
                connection=CONNECTION, owner_id=owner_id, page_number=int(page_number), page_size=int(page_size) 
            )
        elif "pageSize" in event["queryStringParameters"]:
            page_size = event["queryStringParameters"]["pageSize"]
            response = get_user_groups(
                connection=CONNECTION, owner_id=owner_id, page_size=int(page_size)
            )
        elif "page" in event["queryStringParameters"]:
            page_number = event["queryStringParameters"]["page"]
            response = get_user_groups(
                connection=CONNECTION, owner_id=owner_id, page_number=int(page_number)
            )
    else:
        response = get_user_groups(connection=CONNECTION, owner_id=owner_id)

    return response
