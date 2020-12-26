""" Delete device group """

import logging
from models.devices import Devices
from models.api_response import LambdaResponse, Message
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="delete_device")

logger = logging.getLogger(__name__)


@tracer.capture_method
def delete_device(device_id: int, connection: Session) -> dict:
    """ Function that delete device group on db """

    try:
        device = (
            connection.query(Devices)
            .filter_by(id=device_id)
            .delete()
        )

        connection.commit()

        if device == 0:
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
