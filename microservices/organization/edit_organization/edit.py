import logging
from models.organizations import Organization, ResponseModel
from models.api_response import (
    LambdaErrorResponse,
    LambdaSuccessResponse,
    Message,
    Data,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer  # type: ignore

tracer = Tracer(service="edit_organization")

logger = logging.getLogger(__name__)


@tracer.capture_method
def edit_organization(owner_id, organization_id, payload, connection: Session):

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

    if org is None:
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
                    data=[
                        ResponseModel(
                            id=org.id,
                            ownerId=org.owner_id,
                            name=org.name,
                            licenseId=org.license_id,
                        )
                    ]
                ),
            )
