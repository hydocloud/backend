import logging

from aws_lambda_powertools import Tracer  # type: ignore
from models.api_response import DataNoList, LambdaResponse, Message
from models.organizations import Organization, ResponseModel
from pydantic import parse_obj_as
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

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
        return LambdaResponse(
            body=(Message(message="Internal server error")).json(), statusCode=500
        ).dict()

    if org is None:
        return LambdaResponse(
            statusCode=403, body=(Message(message="Forbidden")).json()
        ).dict()
    else:
        if "name" in payload:
            org.name = payload["name"]
        if "licenseId" in payload:
            org.license_id = payload["licenseId"]
            connection.commit()
            obj = parse_obj_as(ResponseModel, org)
            # Call user group
            return LambdaResponse(
                statusCode=201,
                body=DataNoList(data=obj).json(by_alias=True),
            ).dict()
