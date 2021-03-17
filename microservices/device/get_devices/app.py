""" Entry point lambda"""

import logging
import json
from aws_lambda_powertools import Tracer
from get import get_devices
from database import init_db
from models.devices import DevicesModelParameters
from models.api_response import LambdaResponse, Message

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
    logger.info(event)

    global CONNECTION

    if CONNECTION is None:
        CONNECTION = init_db()

    try:
        if (
            "pathParameters" in event
            and event["pathParameters"] is not None
            and "deviceId" in event["pathParameters"]
        ):
            event["queryStringParameters"]["deviceId"] = event["pathParameters"][
                "deviceId"
            ]
        parameters = DevicesModelParameters.parse_obj(event["queryStringParameters"])
        print(parameters)

    except Exception as err:
        print(err)
        logger.error(err)
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()

    response = get_devices(
        connection=CONNECTION,
        device_id=parameters.deviceId,
        device_group_id=parameters.deviceGroupId,
        organization_id=parameters.organizationId,
        page_number=parameters.pageNumber,
        page_size=parameters.pageSize,
    )

    return response
