import database
import os
import logging
import json
from create import create_user_groups
from models.users import UserGroupsApiInput
from models.api_response import Message, LambdaResponse
from database import init_db
from aws_lambda_powertools import Tracer
from pydantic import ValidationError


tracer = Tracer(service="create_user_group")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

CONNECTION = None


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    global CONNECTION

    if CONNECTION == None:
        CONNECTION = init_db()

    try:
        owner_id = "ddd6de86-52be-447b-a8e2-54f40fa78cd1"#event["requestContext"]["authorizer"]["lambda"]["sub"]
        payload = json.loads(event["body"])
        m = UserGroupsApiInput.parse_obj(payload)
        response = create_user_groups(owner_id, m, CONNECTION)
    except ValidationError:
        logger.error("Validation input error")
        return LambdaResponse(
            statusCode = 400,
            body=Message(message="Bad request").json()
        ).dict

    return response
