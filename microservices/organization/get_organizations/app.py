import database
import os
import logging
import json
from get import get_organization
from models.organizations import OrganizationBase
from aws_lambda_powertools import Tracer

tracer = Tracer(service="get_organization")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    
    if 'id' in event['pathParameters']:
        owner_id = 'e12c1545-1362-4162-9c3b-ebe2e20f2e57'
        organization_id = event['pathParameters']['id']
        response = get_organization(owner_id, organization_id)
    # else:
    #     response = get_organizations()

    return {
        "statusCode": response.statusCode,
        "body": response.body.json()
    }