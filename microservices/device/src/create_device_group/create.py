""" Create device groups """

import logging
import datetime
from models.devices import (
    DeviceGroups,
    DeviceGroupsApiInput,
    DeviceGroupsModelShort,
)
from models.api_response import LambdaResponse, DataNoList, Message
from pydantic import ValidationError, parse_obj_as
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="create_device_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def create_device_groups(
    owner_id: str, payload: DeviceGroupsApiInput, connection: Session
) -> dict:
    """ Function that create device group on db """

    try:
        device_groups = DeviceGroups(
            name=payload.name,
            organization_id=payload.organizationId,
            owner_id=owner_id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        connection.add(device_groups)
        connection.commit()
        connection.refresh(device_groups)

        body = DataNoList(
            data=parse_obj_as(DeviceGroupsModelShort, device_groups)
        ).json(exclude_none=True, by_alias=True)

        return LambdaResponse(statusCode=201, body=body).dict()

    except SQLAlchemyError as err:
        logger.error(err)
        connection.rollback()
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server Error").json()
        ).dict()
    except ValidationError as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()
