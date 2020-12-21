""" Create user groups """

import logging
import datetime
from typing import List
from models.users import (
    UserGroups,
    UserBelongUserGroups,
    UserGroupsApiInput,
    UserGroupsModelShort,
)
from models.api_response import LambdaResponse, DataModel, UserGroupsList, Message
from pydantic import ValidationError, parse_obj_as
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="create_user_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def create_user_groups(
    owner_id: str, payload: UserGroupsApiInput, connection: Session
) -> LambdaResponse:
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
        body = DataModel(
            data=UserGroupsList(
                userGroups=parse_obj_as(List[UserGroupsModelShort], [user_groups])
            )
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
