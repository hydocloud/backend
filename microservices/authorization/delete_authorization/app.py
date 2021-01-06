import logging
from delete import delete_authorization
from models.api_response import Message, LambdaResponse
from database import init_db
from aws_lambda_powertools import Tracer


tracer = Tracer(service="delete_authorization")

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
        authorization_id = event["pathParameters"]["id"]
        response = delete_authorization(
            authorization_id=authorization_id, connection=CONNECTION
        )
    except KeyError as err:
        logger.error(err)
        logger.error("Validation input error")
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()

    return response
