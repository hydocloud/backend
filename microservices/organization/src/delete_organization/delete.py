from models.organizations import Organization
from models.api_response import (
    LambdaErrorResponse,
    LambdaSuccessResponseWithoutData,
    Message,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
import logging
from aws_lambda_powertools import Tracer  # type: ignore

tracer = Tracer(service="delete_organization")

logger = logging.getLogger(__name__)


@tracer.capture_method
def delete_organization(owner_id: str, organization_id: str, connection: Session):

    try:
        res = (
            connection.query(Organization)
            .filter_by(owner_id=owner_id, id=organization_id)
            .delete()
        )
        logger.info(res)
        connection.commit()
        if res == 0:
            return LambdaSuccessResponseWithoutData(
                statusCode=404, body=(Message(message="Not found"))
            )
        # Call user group
        return LambdaSuccessResponseWithoutData(
            statusCode=201, body=(Message(message="ok"))
        )
    except SQLAlchemyError as e:
        logger.error(e)
        connection.rollback()
        return LambdaErrorResponse(
            body=(Message(message="Internal Server Error")), statusCode=500
        )
