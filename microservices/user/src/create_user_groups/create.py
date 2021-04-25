""" Create user groups """

import datetime
import logging
from typing import List

from aws_lambda_powertools import Tracer  # type: ignore
from models.api_response import Data, LambdaResponse, Message
from models.users import (
    UserBelongUserGroups,
    UserGroups,
    UserGroupsApiInput,
    UserGroupsModelShort,
)
from pydantic import ValidationError, parse_obj_as
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

tracer = Tracer(service="create_user_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def create_user_groups(
    owner_id: str, payload: UserGroupsApiInput, connection: Session
) -> dict:
    """ Function that create user group on db """

    try:
        user_groups = UserGroups(
            name=payload.name,
            organization_id=payload.organizationId,
            owner_id=owner_id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        connection.add(user_groups)
        connection.commit()
        connection.refresh(user_groups)

        # Add user to his own group
        user_group_belong_users = UserBelongUserGroups(
            user_id=owner_id,
            user_group_id=user_groups.id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        connection.add(user_group_belong_users)
        connection.commit()
        body = Data(data=parse_obj_as(List[UserGroupsModelShort], [user_groups])).json(
            exclude_none=True, by_alias=True
        )

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
