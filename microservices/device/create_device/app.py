import logging
import json
from create import create_device
from models.devices import DevicesApiInput
from database import init_db
from aws_lambda_powertools import Tracer


tracer = Tracer(service="create_device")

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

    user_id = event["requestContext"]["authorizer"]["lambda"]["sub"]
    payload = json.loads(event["body"])
    payload = DevicesApiInput.parse_obj(payload)
    response = create_device(user_id, payload, CONNECTION)
    logger.info(response)
    return response
