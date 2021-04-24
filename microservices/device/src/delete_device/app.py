import logging

from aws_lambda_powertools import Tracer
from database import init_db
from delete import delete_device
from models.api_response import LambdaResponse, Message
from pydantic import ValidationError

tracer = Tracer(service="delete_device")

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
        device_id = event["pathParameters"]["id"]
        response = delete_device(device_id=device_id, connection=CONNECTION)
    except ValidationError:
        logger.error("Validation input error")
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()

    return response
