import json
import logging
from typing import Optional, Tuple

from aws_lambda_powertools import Tracer
from create import create_device_groups
from database import init_db
from models.api_response import LambdaResponse, Message
from models.devices import DeviceGroupsApiInput
from pydantic import ValidationError

tracer = Tracer(service="create_device_group")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

CONNECTION = None


def parse_input(event: dict) -> Tuple[dict, Optional[str]]:
    """ Parse input to check if it's came from api or sqs """
    try:
        owner_id = event["requestContext"]["authorizer"]["lambda"]["sub"]
        message = json.loads(event["body"])
        DeviceGroupsApiInput.parse_obj(message)
        return json.loads(event["body"]), owner_id
    except (ValidationError, KeyError) as err:
        logger.info(err)
    try:
        logger.info(type(event["Records"][0]["body"]))
        message = json.loads(event["Records"][0]["body"])
        owner_id = message["ownerId"]
        del message["ownerId"]
        return message, owner_id
    except (ValidationError, KeyError) as err:
        logger.info(err)

    return {}, None


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    logger.info(event)
    global CONNECTION

    if CONNECTION is None:
        CONNECTION = init_db()

    try:
        payload, owner_id = parse_input(event)
        if len(payload) == 0 and owner_id is None:
            return
        m = DeviceGroupsApiInput.parse_obj(payload)
        response = create_device_groups(owner_id, m, CONNECTION)
    except ValidationError:
        logger.error("Validation input error")
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict

    return response
