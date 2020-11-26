from models.organizations import Organization, OrganizationsList, ResponseModel
from models.api_response import LambdaErrorResponse, LambdaSuccessResponseWithoutData, Message, Data
from sqlalchemy.exc import SQLAlchemyError
import logging
from database import init_db
import datetime
from aws_lambda_powertools import Tracer

tracer = Tracer(service="delete_organization")

logger = logging.getLogger(__name__)

conn = None

@tracer.capture_method
def delete_organization(owner_id, organization_id):
    global conn

    if conn == None:
        conn = init_db()
        
    try:
        res = conn.query(Organization).filter_by(
            owner_id=owner_id,
            id=organization_id
        ).delete()
        logger.info(res)
        conn.commit()
        if res == 0:
            return LambdaSuccessResponseWithoutData(
                statusCode=404, 
                body=(
                    Message(message="Not found")
                )
            )
        # Call user group
        return LambdaSuccessResponseWithoutData(
            statusCode=201, 
            body=(
                Message(message="ok")
            )
        )
    except SQLAlchemyError as e:
        logger.error(e)  
        conn.rollback()   
        return LambdaErrorResponse(
            body=(
                Message(message="Internal Server Error")
            ), 
            statusCode=500
        )
