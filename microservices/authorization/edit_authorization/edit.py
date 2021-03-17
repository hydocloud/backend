""" Edit authorization """

import logging
from typing import List
from pydantic import parse_obj_as
from models.authorization import Authorization, AuthorizationModelApiInput
from models.api_response import (
    LambdaResponse,
    Message,
    DataModel,
    AuthorizationModelShort,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="edit_authorization")

logger = logging.getLogger(__name__)


@tracer.capture_method
def edit_authorization(
    authorization_id: str, payload: AuthorizationModelApiInput, connection: Session
) -> dict:
    """ Edit authorization """

    try:
        authorization = (
            connection.query(Authorization).filter_by(id=authorization_id).first()
        )
        logger.info(authorization)

    except (SQLAlchemyError, AttributeError) as e:
        logger.error(e)
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()

    if authorization is None:
        return LambdaResponse(
            statusCode=404, body=(Message(message="Not found")).json()
        ).dict()
    else:
        # Logic to perform authorization validation

        authorization.user_id = payload.userId
        authorization.device_id = payload.deviceId
        authorization.access_limit = payload.accessLimit
        authorization.start_time = payload.startTime
        authorization.end_time = payload.endTime
        connection.commit()
        m = parse_obj_as(List[AuthorizationModelShort], [authorization])

        body = DataModel(
            data=m, total=None, totalPages=None, nextPage=None, previousPage=None
        ).json(exclude_none=True, by_alias=True)

        return LambdaResponse(statusCode=201, body=body).dict()
