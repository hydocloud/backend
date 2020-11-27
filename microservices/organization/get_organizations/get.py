from models.organizations import Organization, OrganizationsList, ResponseModel
from models.api_response import LambdaErrorResponse, LambdaSuccessResponseWithoutData, LambdaSuccessResponse, Message, Data
from sqlalchemy.exc import SQLAlchemyError
import logging
from database import init_db
import datetime
from aws_lambda_powertools import Tracer
from sqlalchemy_paginator import Paginator, exceptions

tracer = Tracer(service="get_organization")

logger = logging.getLogger(__name__)

conn = None

@tracer.capture_method
def get_organization(owner_id, organization_id):
    global conn

    if conn == None:
        conn = init_db()
        
    try:
        org = conn.query(Organization).filter_by(
            owner_id=owner_id,
            id=organization_id
        ).first()
        logger.info(org)
        if org == None:
            return LambdaErrorResponse(
                statusCode=404, 
                body=(
                    Message(message="Not found")
                )
            )
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
        return LambdaErrorResponse(
            body=(
                Message(message="Internal Server Error")
            ), 
            statusCode=500
        )

@tracer.capture_method
def get_organizations(owner_id, page_number: int = 1):
    global conn

    if conn == None:
        conn = init_db()
        
    try:
        res = conn.query(Organization).filter_by(owner_id=owner_id)
        paginator = Paginator(res, 5)
        page = paginator.page(page_number)
        orgs = []

        for org in page.object_list:
            orgs.append(
                ResponseModel(id=org.id, ownerId=org.owner_id, name=org.name, licenseId=org.license_id)
            )

        response = LambdaSuccessResponse(
            statusCode=201, 
            body=Data(
                data = OrganizationsList(
                    organizations=orgs,
                    total=page.paginator.count,
                    totalPages=page.paginator.total_pages
                )
            )
        )
        if page.has_next: # and page.next_page_number <= page.paginator.total_pages:
            logger.info("Actual {}, next {}, is {}".format(page_number, page.next_page_number, page.has_next))
            response.body.data.nextPage = page.next_page_number
        if page.has_previous: #and page.previous_page_number != 0:
            response.body.data.previousPage = page.previous_page_number
        
        return response

    except (SQLAlchemyError, exceptions.PageNotAnInteger) as e:
        logger.error(e)  
        return LambdaErrorResponse(
            body=(
                Message(message="Internal Server Error")
            ), 
            statusCode=500
        )
    except exceptions.InvalidPage as e:
        logger.error(e)   
        return LambdaErrorResponse(
            body=(
                Message(message="Bad Request")
            ), 
            statusCode=400
        )

    except exceptions.EmptyPage as e:
        return LambdaSuccessResponse(
            statusCode=201, 
            body=Data(
                data = OrganizationsList(
                    organizations=[]
                )
            )
        )
