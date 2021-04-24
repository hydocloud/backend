""" Delete device group """

import logging

from aws_lambda_powertools import Tracer
from models.api_response import LambdaResponse, Message
from models.devices import DeviceGroups
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

tracer = Tracer(service="delete_device_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def delete_device_groups(
    owner_id: str, device_group_id: int, connection: Session
) -> LambdaResponse:
    """ Function that delete device group on db """

    try:
        device_group = (
            connection.query(DeviceGroups)
            .filter_by(owner_id=owner_id, id=device_group_id)
            .delete()
        )

        connection.commit()

        if device_group == 0:
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
