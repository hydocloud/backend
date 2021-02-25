""" Entry point lambda"""

import logging
import json
from aws_lambda_powertools import Tracer
from get import get_devices
from database import init_db

tracer = Tracer(service="get_devices")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
CONNECTION = None


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    response = {"statusCode": 400, "body": json.dumps({"message": "Bad request"})}
    """
    Based on both path parameters or query parameters chose if
    device require info about one device group or multiple
    """

    global CONNECTION

    if CONNECTION is None:
        CONNECTION = init_db()

    if (
        "pathParameters" in event
        and event["pathParameters"] is not None
        and "id" in event["pathParameters"]
    ):
        device_id = event["pathParameters"]["id"]
        device_group_id = event["queryStringParameters"]["deviceGroupId"]
        response = get_devices(
            connection=CONNECTION, device_group_id=device_group_id, device_id=device_id
        )
    elif (
        "queryStringParameters" in event and event["queryStringParameters"] is not None
    ):
        if (
            "pageSize" in event["queryStringParameters"]
            and "page" in event["queryStringParameters"]
            and "deviceGroupId" in event["queryStringParameters"]
        ):
            print(event["queryStringParameters"])
            page_number = int(event["queryStringParameters"]["page"])
            page_size = int(event["queryStringParameters"]["pageSize"])
            device_group_id = int(event["queryStringParameters"]["deviceGroupId"])
            response = get_devices(
                connection=CONNECTION,
                device_group_id=device_group_id,
                page_number=page_number,
                page_size=page_size,
            )
        elif (
            "pageSize" in event["queryStringParameters"]
            and "deviceGroupId" in event["queryStringParameters"]
        ):
            page_size = event["queryStringParameters"]["pageSize"]
            device_group_id = int(event["queryStringParameters"]["deviceGroupId"])
            response = get_devices(
                connection=CONNECTION,
                device_group_id=device_group_id,
                page_size=int(page_size),
            )
        elif (
            "page" in event["queryStringParameters"]
            and "deviceGroupId" in event["queryStringParameters"]
        ):
            page_number = int(event["queryStringParameters"]["page"])
            device_group_id = int(event["queryStringParameters"]["deviceGroupId"])
            response = get_devices(
                connection=CONNECTION,
                device_group_id=device_group_id,
                page_number=int(page_number),
            )

    return response
