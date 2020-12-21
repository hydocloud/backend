"""
Module get organization to have list of organizations filter by owner_id
You can select on single organization or multiple organization
"""

import logging
from models.organizations import Organization, OrganizationsList, ResponseModel
from models.api_response import (
    LambdaErrorResponse,
    LambdaSuccessResponse,
    Message,
    Data,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

from aws_lambda_powertools import Tracer
from sqlalchemy_paginator import Paginator, exceptions

tracer = Tracer(service="get_organization")

logger = logging.getLogger(__name__)


@tracer.capture_method
def get_organization(connection: Session, owner_id: str, organization_id: str):
    """ Get data about one organization"""

    try:
        org = (
            connection.query(Organization)
            .filter_by(owner_id=owner_id, id=organization_id)
            .first()
        )
        logger.info(org)
        if org is None:
            return LambdaErrorResponse(
                statusCode=404, body=(Message(message="Not found"))
            )
        # Call user group
        return LambdaSuccessResponse(
            statusCode=201,
            body=Data(
                data=OrganizationsList(
                    organizations=[
                        ResponseModel(
                            id=org.id,
                            ownerId=org.owner_id,
                            name=org.name,
                            licenseId=org.license_id,
                        )
                    ]
                )
            ),
        )
    except SQLAlchemyError as err:
        logger.error(err)
        return LambdaErrorResponse(
            body=(Message(message="Internal Server Error")), statusCode=500
        )


@tracer.capture_method
def get_organizations(
    connection: Session, owner_id: str, page_number: int = 1, page_size: int = 5,
):
    """ Return all organizations that belong to user"""

    try:
        res = connection.query(Organization).filter_by(owner_id=owner_id)
        paginator = Paginator(res, page_size)
        page = paginator.page(page_number)
        orgs = []

        for org in page.object_list:
            orgs.append(
                ResponseModel(
                    id=org.id,
                    ownerId=org.owner_id,
                    name=org.name,
                    licenseId=org.license_id,
                )
            )

        response = LambdaSuccessResponse(
            statusCode=201,
            body=Data(
                data=OrganizationsList(
                    organizations=orgs,
                    total=page.paginator.count,
                    totalPages=page.paginator.total_pages,
                )
            ),
        )

        if page.has_next():
            response.body.data.nextPage = page.next_page_number
        if page.has_previous():
            response.body.data.previousPage = page.previous_page_number

        return response

    except (SQLAlchemyError, exceptions.PageNotAnInteger) as err:
        logger.error(err)
        return LambdaErrorResponse(
            body=(Message(message="Internal Server Error")), statusCode=500
        )

    except exceptions.EmptyPage as err:
        logger.error(err)
        return LambdaSuccessResponse(
            statusCode=201, body=Data(data=OrganizationsList(organizations=[]))
        )

    except exceptions.InvalidPage as err:
        logger.error(err)
        return LambdaErrorResponse(
            body=(Message(message="Bad Request")), statusCode=400
        )
