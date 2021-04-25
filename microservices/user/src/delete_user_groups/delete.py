""" Delete user group """

import logging

from aws_lambda_powertools import Tracer  # type: ignore
from models.api_response import LambdaResponse, Message
from models.users import UserGroups
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

tracer = Tracer(service="delete_user_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def delete_user_groups(owner_id: str, user_group_id: int, connection: Session) -> dict:
    """ Function that delete user group on db """

    try:
        user_group = (
            connection.query(UserGroups)
            .filter_by(owner_id=owner_id, id=user_group_id)
            .delete()
        )

        connection.commit()

        if user_group == 0:
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
