import database
import os
import logging
import json
from create import main as create_organization
from models.organizations import OrganizationBase

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

def handler(event, context):

    payload = json.loads(event['body'])
    OrganizationBase.parse_obj(payload)
    response = create_organization(payload)

    return json.loads(response.json())
