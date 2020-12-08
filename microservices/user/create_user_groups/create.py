""" Create user groups """

import logging
import datetime
import json
from models.users import UserGroups, UserBelongUserGroups, UserGroupsApiInput
from models.api_response import LambdaResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="create_user_group")

logger = logging.getLogger(__name__)


@tracer.capture_method
def create_user_groups(owner_id: str, payload: UserGroupsApiInput, connection: Session) -> LambdaResponse:
    """ Function that create user group on db """

    try:
        user_groups = UserGroups(
            name=payload.name,
            organization_id=payload.organizationId,
            owner_id=owner_id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        connection.add(user_groups)
        connection.commit()
        connection.refresh(user_groups)

        # Add user to his own group
        user_group_belong_users = UserBelongUserGroups(
            user_id=owner_id,
            user_group_id=user_groups.id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        connection.add(user_group_belong_users)
        connection.commit()

        return LambdaResponse(
            statusCode=201,
            body= {
                "data": {
                    "userGroups": [
                        {
                            "id": user_groups.id,
                            "name": user_groups.name,
                            "organizationId": user_groups.organization_id,
                            "ownerId": str(user_groups.owner_id)
                        }
                    ]
                }
            },
        )
    except SQLAlchemyError as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode = 500,
            body={
                "message": "Internal server error"
            }
        )
    except ValidationError as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode = 400,
            body={
                "message": "Bad request"
            }
        )
