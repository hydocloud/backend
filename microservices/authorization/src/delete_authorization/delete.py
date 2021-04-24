""" Delete authorization group """

import logging

from aws_lambda_powertools import Tracer
from models.api_response import LambdaResponse, Message
from models.authorization import Authorization
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

tracer = Tracer(service="delete_authorization")

logger = logging.getLogger(__name__)


@tracer.capture_method
def delete_authorization(authorization_id: int, connection: Session) -> dict:
    """ Function that delete authorization group on db """

    try:
        authorization = (
            connection.query(Authorization).filter_by(id=authorization_id).delete()
        )

        connection.commit()

        if authorization == 0:
            status_code = 404
            message = "Not found"
        else:
            status_code = 201
            message = "Ok"

        return LambdaResponse(
            statusCode=status_code, body=Message(message=message).json()
        ).dict()
    except SQLAlchemyError as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()
