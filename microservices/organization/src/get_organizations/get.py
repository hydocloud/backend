"""
Module get organization to have list of organizations filter by owner_id
You can select on single organization or multiple organization
"""

import logging
from typing import List

from aws_lambda_powertools import Tracer  # type: ignore
from models.api_response import Data, LambdaResponse, Message
from models.organizations import Organization, ResponseModel
from pydantic import parse_obj_as
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from sqlalchemy_paginator import Paginator, exceptions  # type: ignore

tracer = Tracer(service="get_organization")

logger = logging.getLogger(__name__)


@tracer.capture_method
def get_organizations(
    connection: Session,
    owner_id: str,
    page_number: int = 1,
    page_size: int = 5,
    organization_id: int = None,
):
    """ Return all organizations that belong to user"""

    try:
        res = connection.query(Organization).filter_by(owner_id=owner_id)
        paginator = Paginator(res, page_size)
        page = paginator.page(page_number)
        m = parse_obj_as(List[ResponseModel], page.object_list)

        body = Data(
            data=m,
            total=page.paginator.count,
            totalPages=page.paginator.total_pages,
            nextPage=(page.next_page_number if page.has_next() else None),
            previousPage=(page.previous_page_number if page.has_previous() else None),
        ).json(by_alias=True)

        return LambdaResponse(statusCode=200, body=body).dict()

    except (SQLAlchemyError, exceptions.PageNotAnInteger) as err:
        logger.error(err)
        return LambdaErrorResponse(
            body=(Message(message="Internal Server Error")).json(), statusCode=500
        ).dict()

    except exceptions.EmptyPage as err:
        logger.error(err)
        return LambdaSuccessResponse(statusCode=201, body=Data(data=[])).dict()

    except exceptions.InvalidPage as err:
        logger.error(err)
        return LambdaErrorResponse(
            body=(Message(message="Bad Request")).json(), statusCode=400
        ).dict
