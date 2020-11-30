import database
import os
import logging
import json
from create import create_organization
from models.organizations import OrganizationBase
from aws_lambda_powertools import Tracer

tracer = Tracer(service="create_organization")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):

    owner_id = event["requestContext"]["authorizer"]["lambda"]["sub"]
    payload = json.loads(event["body"])
    OrganizationBase.parse_obj(payload)
    response = create_organization(owner_id, payload)

    return {"statusCode": response.statusCode, "body": response.body.json()}
