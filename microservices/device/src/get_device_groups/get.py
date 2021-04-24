"""
Module get device_group to have list of device_groups filter by owner_id
You can select on single device_group or multiple device_group
"""

import logging
from typing import List

from aws_lambda_powertools import Tracer
from models.api_response import Data, LambdaResponse, Message
from models.devices import DeviceGroups, DeviceGroupsModelShort
from pydantic import ValidationError, parse_obj_as
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from sqlalchemy_paginator import Paginator

tracer = Tracer(service="get_device_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def get_device_groups(
    connection: Session,
    owner_id: str,
    device_group_id: str = None,
    page_number: int = 1,
    page_size: int = 5,
) -> dict:
    """ Get data about one device group or multiple"""

    try:
        if device_group_id is None:
            res = connection.query(DeviceGroups).filter(
                DeviceGroups.owner_id == owner_id
            )
        else:
            res = connection.query(DeviceGroups).filter(
                DeviceGroups.owner_id == owner_id, DeviceGroups.id == device_group_id
            )

        paginator = Paginator(res, page_size)
        page = paginator.page(page_number)

        m = parse_obj_as(List[DeviceGroupsModelShort], page.object_list)

        status_code = 200
        body = Data(
            data=m,
            total=page.paginator.count,
            totalPages=page.paginator.total_pages,
            nextPage=(page.next_page_number if page.has_next() else None),
            previousPage=(page.previous_page_number if page.has_previous() else None),
        ).json(by_alias=True)

        return LambdaResponse(statusCode=status_code, body=body).dict()

    except (SQLAlchemyError, ValidationError) as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()
