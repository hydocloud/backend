"""
Module get user_group to have list of user_groups filter by owner_id
You can select on single user_group or multiple user_group
"""

import logging
from typing import List
from models.users import UserGroups, UserBelongUserGroups, UserGroupsModelShort
from models.api_response import LambdaResponse, DataModel, Message
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

from aws_lambda_powertools import Tracer  # type: ignore
from sqlalchemy_paginator import Paginator  # type: ignore
from pydantic import ValidationError, parse_obj_as

tracer = Tracer(service="get_user_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def get_user_groups(
    connection: Session,
    owner_id: str,
    user_group_id: str = None,
    page_number: int = 1,
    page_size: int = 5,
) -> dict:
    """ Get data about one user group or multiple"""

    try:
        if user_group_id is None:
            res = (
                connection.query(UserGroups)
                .join(UserBelongUserGroups)
                .filter(UserBelongUserGroups.user_id == owner_id)
            )
        else:
            res = (
                connection.query(UserGroups)
                .join(UserBelongUserGroups)
                .filter(
                    UserBelongUserGroups.user_id == owner_id,
                    UserGroups.id == user_group_id,
                )
            )

        paginator = Paginator(res, page_size)
        page = paginator.page(page_number)

        m = parse_obj_as(List[UserGroupsModelShort], page.object_list)

        if len(m) == 0:
            status_code = 404
            body = Message(message="Not found").json()
        else:
            status_code = 200
            body = DataModel(
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
