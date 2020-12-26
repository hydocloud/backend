""" Edit device """

import logging
from typing import List
from pydantic import parse_obj_as
from models.devices import Devices, DevicesEditInput, DevicesModelShort
from models.api_response import LambdaResponse, Message, DevicesDataModel, DevicesList
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="edit_device")

logger = logging.getLogger(__name__)


@tracer.capture_method
def edit_device(device_id: str, payload: DevicesEditInput, connection: Session) -> dict:
    """ Edit device """

    try:
        device = connection.query(Devices).filter_by(id=device_id).first()
        logger.info(device)

    except (SQLAlchemyError, AttributeError) as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()

    if device is None:
        return LambdaResponse(
            statusCode=404, body=(Message(message="Not found")).json()
        ).dict()
    else:
        device.name = payload.name
        device.device_group_id = payload.deviceGroupId
        connection.commit()
        m = DevicesList(
            devices=parse_obj_as(List[DevicesModelShort], [device])
        )

        body = DevicesDataModel(
            data=m, total=None, totalPages=None, nextPage=None, previousPage=None
        ).json(exclude_none=True, by_alias=True)

        return LambdaResponse(statusCode=201, body=body).dict()
