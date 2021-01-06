"""
Module get devices to have list of devices filter by owner_id
You can select on single devices or multiple devices
"""

import logging
from typing import List
from models.devices import Devices, DevicesModelShort
from models.api_response import LambdaResponse, DevicesList, DevicesDataModel, Message
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

from aws_lambda_powertools import Tracer
from sqlalchemy_paginator import Paginator
from sqlalchemy_paginator.exceptions import EmptyPage
from pydantic import ValidationError, parse_obj_as

tracer = Tracer(service="get_devices")

logger = logging.getLogger(__name__)


@tracer.capture_method
def get_devices(
    connection: Session,
    device_id: str = None,
    device_group_id: int = None,
    page_number: int = 1,
    page_size: int = 5,
) -> dict:
    """ Get data about one device group or multiple"""
    try:
        if device_id is None:
            res = connection.query(Devices).filter(
                Devices.device_group_id == device_group_id
            )
        else:
            res = connection.query(Devices).filter(
                Devices.device_group_id == device_group_id, Devices.id == device_id
            )

        paginator = Paginator(res, page_size)
        page = paginator.page(page_number)

        m = DevicesList(devices=parse_obj_as(List[DevicesModelShort], page.object_list))

        if len(m.devices) == 0:
            status_code = 404
            body = Message(message="Not found").json()
        else:
            status_code = 200
            body = DevicesDataModel(
                data=m,
                total=page.paginator.count,
                totalPages=page.paginator.total_pages,
                nextPage=(page.next_page_number if page.has_next() else None),
                previousPage=(
                    page.previous_page_number if page.has_previous() else None
                ),
            ).json(by_alias=True)

        return LambdaResponse(statusCode=status_code, body=body).dict()

    except (SQLAlchemyError, ValidationError) as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()
    except EmptyPage as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()