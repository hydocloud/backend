import datetime
import json
import logging
import os
from os import environ

import boto3
from aws_lambda_powertools import Tracer
from botocore.exceptions import ClientError, ParamValidationError
from models.api_response import DataNoList, LambdaResponse, Message
from models.devices import Devices, DevicesApiInput, DevicesModelShort, DevicesModelShortPublicKey
from pydantic import ValidationError, parse_obj_as
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.session import Session

tracer = Tracer(service="create_device")

logger = logging.getLogger(__name__)


def get_key(secret_manager=None) -> str:
    secret_name = environ["SECRET_NAME"]
    if secret_manager is None:
        session = boto3.session.Session()
        secret_manager = session.client(service_name="secretsmanager")

    try:
        get_secret_value_response = secret_manager.get_secret_value(
            SecretId=secret_name
        )
        logger.debug(f'key: {get_secret_value_response["SecretString"]}')
        get_secret_value_response = json.loads(get_secret_value_response["SecretString"])
        return get_secret_value_response["publicKey"]
    except ClientError as err:
        logger.error(err)
        raise err


def create_authorization(device_id: int, user_id: str):
    queue_url = os.environ["QUEUE_URL"] if "QUEUE_URL" in os.environ else None
    sqs = boto3.client("sqs")
    message = json.dumps({"deviceId": device_id, "userId": user_id})
    try:
        queue = queue_url
        sqs.send_message(QueueUrl=queue, MessageBody=message)
    except (ClientError, ParamValidationError, ValueError) as err:
        logger.error(err)
        raise err


@tracer.capture_method
def create_device(user_id: str, payload: DevicesApiInput, connection: Session) -> dict:
    try:
        device = Devices(
            name=payload.name,
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
        device_short = parse_obj_as(DevicesModelShort, device)
        device_short = device_short.dict()
        device_short["publicKey"] = get_key()
        device_short_public_key = parse_obj_as(DevicesModelShortPublicKey, device_short)
        body = DataNoList(data=device_short_public_key).json(
            by_alias=True
        )
        return LambdaResponse(statusCode=201, body=body).dict()
    except (IntegrityError) as err:
        logger.error(err)
        connection.rollback()
        return LambdaResponse(
            statusCode=409, body=Message(message="Conflict").json()
        ).dict()
    except (SQLAlchemyError) as err:
        logger.error(err)
        connection.rollback()
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
