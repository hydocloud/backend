import json
import logging

from aws_lambda_powertools import Tracer  # type: ignore
from edit import edit_user_group  # type: ignore
from models.api_response import LambdaResponse, Message
from models.users import UserGroupsApiEditInput
from pydantic import ValidationError

from database import init_db

tracer = Tracer(service="edit_user_group")

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
        user_group_id = event["pathParameters"]["id"]
        m = UserGroupsApiEditInput.parse_obj(payload)
        response = edit_user_group(owner_id, user_group_id, m, CONNECTION)
        logger.info(response)
    except ValidationError:
        logger.error("Validation input error")
        return LambdaResponse(
            statusCode=400, body=(Message(message="Bad request")).json()
        ).dict()

    return response
