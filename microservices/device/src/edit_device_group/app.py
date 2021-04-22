import logging
import json
from pydantic import ValidationError
from edit import edit_device_group
from models.devices import DeviceGroupsApiEditInput
from models.api_response import Message, LambdaResponse
from database import init_db
from aws_lambda_powertools import Tracer

tracer = Tracer(service="edit_device_group")

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

    try:
        owner_id = event["requestContext"]["authorizer"]["lambda"]["sub"]
        payload = json.loads(event["body"])
        device_group_id = event["pathParameters"]["id"]
        m = DeviceGroupsApiEditInput.parse_obj(payload)
        response = edit_device_group(owner_id, device_group_id, m, CONNECTION)
        logger.info(response)
    except ValidationError:
        logger.error("Validation input error")
        return LambdaResponse(
            statusCode=400, body=(Message(message="Bad request")).json()
        ).dict()

    return response
