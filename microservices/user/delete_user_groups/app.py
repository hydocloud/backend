import database
import os
import logging
import json
from delete import delete_user_groups
from models.users import UserGroupsApiInput
from models.api_response import Message, LambdaResponse
from database import init_db
from aws_lambda_powertools import Tracer
from pydantic import ValidationError


tracer = Tracer(service="delete_user_group")

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
        owner_id = event["requestContext"]["authorizer"]["lambda"]["sub"]
        user_group_id = event["pathParameters"]["id"]
        response = delete_user_groups(
            owner_id=owner_id, user_group_id=user_group_id, connection=CONNECTION
        )
    except ValidationError:
        logger.error("Validation input error")
        return LambdaResponse(
            statusCode = 400,
            body= Message(message="Bad request").json()
        ).dict()

    return response
