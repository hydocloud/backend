from models.organizations import Organization, OrganizationsList, ResponseModel
from models.api_response import LambdaErrorResponse, LambdaSuccessResponse, Message, Data
from sqlalchemy.exc import SQLAlchemyError
import logging
from database import init_db
import datetime
from aws_lambda_powertools import Tracer

tracer = Tracer(service="create_organization")

logger = logging.getLogger(__name__)

conn = None

@tracer.capture_method
def create_organization(owner_id, payload):
    global conn

    if conn == None:
        conn = init_db()

    name = None
    license_id = None
    try:
        name = payload["name"]
        license_id = payload["licenseId"]
    except KeyError as e:
        logger.error(e)
        return LambdaErrorResponse(
            body=(
                Message(message="Bad request")
            ), 
            statusCode=400
        )
        
    try:
        org = Organization(owner_id=owner_id, name=name, license_id=license_id, created_at=datetime.datetime.utcnow(), updated_at=datetime.datetime.utcnow())
        conn.add(org)
        conn.commit()
        conn.refresh(org)
        # Call user group
        return LambdaSuccessResponse(
            statusCode=201, 
            body=Data(
                data = OrganizationsList(
                    organizations=[
                        ResponseModel(id=org.id, ownerId=org.owner_id, name=org.name, licenseId=org.license_id)
                    ]
                )
            )
        )
    except SQLAlchemyError as e:
        logger.error(e)  
        conn.rollback()   
        return LambdaErrorResponse(
            body=(
                Message(message="Bad request")
            ), 
            statusCode=500
        )
