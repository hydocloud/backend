"""
Module get authorizations to have list of authorizations filter by owner_id
You can select on single authorizations or multiple authorizations
"""

import logging
from typing import List
from models.authorization import Authorization, AuthorizationModelShort
from models.api_response import LambdaResponse, AuthorizationList, DataModel, Message
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from authorization_filter import AuthorizationFilter
from aws_lambda_powertools import Tracer
from sqlalchemy_paginator import Paginator
from sqlalchemy_paginator.exceptions import EmptyPage
from pydantic import ValidationError, parse_obj_as

tracer = Tracer(service="get_authorizations")

logger = logging.getLogger(__name__)


@tracer.capture_method
def get_authorizations(
    connection: Session,
    page_number: int = 1,
    page_size: int = 5,
    device_id: int = None,
    user_id: str = None,
    authorization_id: int = None
) -> dict:
    """ Get data about one authorization group or multiple"""
    try:

        x = AuthorizationFilter(connection.query(Authorization), user_id, device_id, authorization_id)
        res = x.build_filter()

        paginator = Paginator(res, page_size)
        page = paginator.page(page_number)

        m = AuthorizationList(
            authorizations=parse_obj_as(List[AuthorizationModelShort], page.object_list)
        )

        if len(m.authorizations) == 0:
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
    except EmptyPage as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()
