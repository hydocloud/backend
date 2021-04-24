import json
import logging

from aws_lambda_powertools import Tracer
from database import init_db
from edit import edit_authorization
from models.api_response import LambdaResponse, Message
from models.authorization import AuthorizationModelApiInput
from pydantic import ValidationError

tracer = Tracer(service="edit_authorization")

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
        payload = json.loads(event["body"])
        authorization_id = event["pathParameters"]["id"]
        m = AuthorizationModelApiInput.parse_obj(payload)
        response = edit_authorization(authorization_id, m, CONNECTION)
        logger.info(response)
    except (ValidationError, json.decoder.JSONDecodeError):
        logger.error("Validation input error")
        return LambdaResponse(
            statusCode=400, body=(Message(message="Bad request")).json()
        ).dict()

    return response
