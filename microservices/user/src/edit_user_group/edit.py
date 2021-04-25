""" Edit user """

import logging
from typing import List
from pydantic import parse_obj_as
from models.users import UserGroups, UserGroupsModelShort
from models.api_response import LambdaResponse, Message, DataModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session  # type: ignore
from aws_lambda_powertools import Tracer  # type: ignore

tracer = Tracer(service="edit_user_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def edit_user_group(
    owner_id: str, user_group_id: str, payload, connection: Session
) -> dict:
    """ Edit user """

    try:
        user_group = (
            connection.query(UserGroups)
            .filter_by(owner_id=owner_id, id=user_group_id)
            .first()
        )
        logger.info(user_group)

    except (SQLAlchemyError, AttributeError) as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()

    if user_group is None:
        return LambdaResponse(
            statusCode=403, body=(Message(message="Forbidden")).json()
        ).dict()
    else:
        user_group.name = payload.name
        connection.commit()
        m = parse_obj_as(List[UserGroupsModelShort], [user_group])

        body = DataModel(
            data=m, total=None, totalPages=None, nextPage=None, previousPage=None
        ).json(exclude_none=True, by_alias=True)

        return LambdaResponse(statusCode=201, body=body).dict()
