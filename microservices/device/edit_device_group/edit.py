""" Edit device """

import logging
from typing import List
from pydantic import parse_obj_as
from models.devices import DeviceGroups, DeviceGroupsModelShort
from models.api_response import LambdaResponse, Message, DataModel, DeviceGroupsList
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="edit_device_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def edit_device_group(
    owner_id: str, device_group_id: str, payload, connection: Session
) -> LambdaResponse:
    """ Edit device """

    try:
        device_group = (
            connection.query(DeviceGroups)
            .filter_by(owner_id=owner_id, id=device_group_id)
            .first()
        )
        logger.info(device_group)

    except (SQLAlchemyError, AttributeError) as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()

    if device_group is None:
        return LambdaResponse(
            statusCode=403, body=(Message(message="Forbidden")).json()
        ).dict()
    else:
        device_group.name = payload.name
        connection.commit()
        m = DeviceGroupsList(
            deviceGroups=parse_obj_as(List[DeviceGroupsModelShort], [device_group])
        )

        body = DataModel(
            data=m, total=None, totalPages=None, nextPage=None, previousPage=None
        ).json(exclude_none=True, by_alias=True)

        return LambdaResponse(statusCode=201, body=body).dict()
