from models.organizations import Organization, OrganizationsList, ResponseModel
from models.api_response import (
    LambdaErrorResponse,
    LambdaSuccessResponse,
    Message,
    Data,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
import logging

import datetime
from aws_lambda_powertools import Tracer

tracer = Tracer(service="edit_organization")

logger = logging.getLogger(__name__)


@tracer.capture_method
def edit_organization(owner_id, organization_id, payload, connection: Session):

    name = None
    license_id = None
    try:
        name = payload["name"]
        license_id = payload["licenseId"]
    except KeyError as e:
        logger.error(e)
        return LambdaErrorResponse(
            body=(Message(message="Bad request")), statusCode=400
        )

    try:
        org = (
            connection.query(Organization)
            .filter_by(owner_id=owner_id, id=organization_id)
            .first()
        )

    except (SQLAlchemyError, AttributeError) as e:
        logger.error(e)
        connection.rollback()
        return LambdaErrorResponse(
            body=(Message(message="Internal server error")), statusCode=500
        )

    if org == None:
        return LambdaErrorResponse(statusCode=403, body=(Message(message="Forbidden")))
    else:
        if "name" in payload:
            org.name = payload["name"]
        if "licenseId" in payload:
            org.license_id = payload["licenseId"]
            connection.commit()
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
