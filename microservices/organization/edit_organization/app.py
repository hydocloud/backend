import database
import os
import logging
import json
from edit import edit_organization
from models.organizations import OrganizationsUpdate
from aws_lambda_powertools import Tracer

tracer = Tracer(service="edit_organization")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):

    owner_id = 'e12c1545-1362-4162-9c3b-ebe2e20f2e57'
    organization_id = event['pathParameters']['id']
    payload = json.loads(event['body'])
    OrganizationsUpdate.parse_obj(payload)
    response = edit_organization(owner_id, organization_id, payload)

    return {
        "statusCode": response.statusCode,
        "body": response.body.data.json()
    }
