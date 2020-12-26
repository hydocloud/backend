import logging
import datetime
import os
import boto3
import json
from typing import List
from pydantic import parse_obj_as, ValidationError
from botocore.exceptions import ClientError
from models.devices import Devices, DevicesModelShort, DevicesApiInput
from models.api_response import LambdaResponse, Message, DevicesDataModel, DevicesList
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="create_device")

logger = logging.getLogger(__name__)
QUEUE_URL = os.environ["QUEUE_URL"] if "QUEUE_URL" in os.environ else None


def create_authorization(device_id: int, user_id: str):
    sqs = boto3.client("sqs")
    message = json.dumps({"deviceId": device_id, "userId": user_id})
    try:
        queue = QUEUE_URL
        sqs.send_message(QueueUrl=queue, MessageBody=message)
    except ClientError as err:
        logger.error(err)
    except ValueError as err:
        logger.error(err)


@tracer.capture_method
def create_device(user_id: str, payload: DevicesApiInput, connection: Session) -> dict:

    try:
        device = Devices(
            serial=payload.serial,
            device_group_id=payload.deviceGroupId,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        connection.add(device)
        connection.commit()
        connection.refresh(device)

        # Create authorization
        create_authorization(device_id=device.id, user_id=user_id)

        body = DevicesDataModel(
            data=DevicesList(
                devices=parse_obj_as(List[DevicesModelShort], [device])
            )
        ).json(exclude_none=True, by_alias=True)

        return LambdaResponse(statusCode=201, body=body).dict()
    except (SQLAlchemyError) as err:
        logger.error(err)
        connection.rollback()
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server Error").json()
        ).dict()
    except (ValidationError, AttributeError) as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()
