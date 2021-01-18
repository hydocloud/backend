""" Create device groups """

import logging
import datetime
from typing import List
from models.authorization import (
    Authorization,
    AuthorizationModelApiInput,
    AuthorizationModelShort,
)
from models.api_response import (
    LambdaResponse,
    DataModel,
    AuthorizationList,
    Message,
)
from pydantic import ValidationError, parse_obj_as
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="create_authorization")

logger = logging.getLogger(__name__)


@tracer.capture_method
def create_authorization(
    payload: AuthorizationModelApiInput, connection: Session
) -> dict:
    """ Function that create authorization on db """

    try:
        # Perform logic to validate authorization type

        authorization = Authorization(
            user_id=payload.userId,
            device_id=payload.deviceId,
            access_limit=payload.accessLimit,
            start_time=payload.startTime,
            end_time=payload.endTime,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        connection.add(authorization)
        connection.commit()
        connection.refresh(authorization)

        body = DataModel(
            data=AuthorizationList(
                authorizations=parse_obj_as(
                    List[AuthorizationModelShort], [authorization]
                )
            )
        ).json(exclude_none=True, by_alias=True)

        return LambdaResponse(statusCode=201, body=body).dict()

    except SQLAlchemyError as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server Error").json()
        ).dict()
    except (ValidationError, AttributeError) as err:
        print(err)
        logger.error(err)
        connection.rollback()
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()
