"""
Module get user_group to have list of user_groups filter by owner_id
You can select on single user_group or multiple user_group
"""

import logging
from models.users import UserGroups, UserBelongUserGroups
from models.api_response import LambdaResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

from aws_lambda_powertools import Tracer
from sqlalchemy_paginator import Paginator, exceptions

tracer = Tracer(service="get_user_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def get_user_groups(
    connection: Session,
    owner_id: str,
    user_group_id: str = None,
    page_number: int = 1,
    page_size: int = 5,
) -> LambdaResponse:
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
        groups = []
        logger.info(len(page.object_list))
        for group in page.object_list:
            groups.append(
                {
                    "id": group.id,
                    "name": group.name,
                    "organizationId": group.organization_id,
                }
            )

        logger.info(
            f"Next {page.next_page_number}, Previous {page.previous_page_number}, Total elements {page.paginator.count}, Total pages {page.paginator.total_pages}"
        )

        if len(groups) == 0:
            status_code = 404
            body = {"Message": "Not found"}
        else:
            status_code = 200
            body = {
                "data": {"userGroups": groups},
                "total": page.paginator.count,
                "totalPages": page.paginator.total_pages,
            }
            if page.has_next():
                body["nextPage"] = page.next_page_number
            if page.has_previous():
                body["previousPage"] = page.previous_page_number

        return LambdaResponse(statusCode=status_code, body=body)

    except SQLAlchemyError as err:
        logger.error(err)
        return LambdaResponse(statusCode=500, body={"Message": "Internal server error"})
