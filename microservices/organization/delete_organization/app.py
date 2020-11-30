import database
import os
import logging
import json
from delete import delete_organization
from models.organizations import OrganizationBase
from aws_lambda_powertools import Tracer

tracer = Tracer(service="delete_organization")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):

    owner_id = event["requestContext"]["authorizer"]["lambda"]["sub"]
    organization_id = event["pathParameters"]["id"]
    response = delete_organization(owner_id, organization_id)

    return {"statusCode": response.statusCode, "body": response.body.json()}
