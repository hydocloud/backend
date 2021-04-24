import json
import logging
from typing import Optional

from aws_lambda_powertools import Tracer
from create import create_authorization
from database import init_db
from models.authorization import AuthorizationModelApiInput
from pydantic import ValidationError

tracer = Tracer(service="create_device_group")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

CONNECTION = None


def parse_input(event: dict) -> Optional[AuthorizationModelApiInput]:
    """ Parse input to check if it's came from api or sqs """
    try:
        message = json.loads(event["body"])
        return AuthorizationModelApiInput.parse_obj(message)
    except (ValidationError, KeyError) as err:
        logger.info(err)
    try:
        logger.info(type(event["Records"][0]["body"]))
        message = json.loads(event["Records"][0]["body"])
        return AuthorizationModelApiInput.parse_obj(message)
    except (ValidationError, KeyError) as err:
        logger.info(err)

    return None


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    logger.info(event)
    global CONNECTION

    if CONNECTION is None:
        CONNECTION = init_db()

    payload = parse_input(event)
    if payload is None:
        return

    response = create_authorization(payload, CONNECTION)
    return response
