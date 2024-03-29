import datetime
import json
import logging
import os

import boto3
from aws_lambda_powertools import Tracer  # type: ignore
from botocore.exceptions import ClientError
from models.api_response import DataNoList, LambdaResponse, Message
from models.organizations import Organization, ResponseModel
from pydantic import parse_obj_as
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

tracer = Tracer(service="create_organization")

logger = logging.getLogger(__name__)
QUEUE_URLS = str(os.environ["QUEUE_URLS"]) if "QUEUE_URLS" in os.environ else ""


def create_user_device_default_group(
    organization_id: int, owner_id: str, name: str = "DEFAULT"
):

    sqs = boto3.client("sqs")
    message = json.dumps(
        {"name": name, "organizationId": organization_id, "ownerId": owner_id}
    )
    try:
        queue_urls = json.loads(QUEUE_URLS)
        for queue in queue_urls:
            sqs.send_message(QueueUrl=queue, MessageBody=message)
    except ClientError as err:
        logger.error(err)
    except ValueError as err:
        logger.error(err)


@tracer.capture_method
def create_organization(owner_id, payload, connection: Session):

    name = None
    license_id = None
    try:
        name = payload["name"]
        license_id = payload["licenseId"]
    except KeyError as e:
        logger.error(e)
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()
    try:
        org = Organization(
            owner_id=owner_id,
            name=name,
            license_id=license_id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        connection.add(org)
        connection.commit()
        connection.refresh(org)

        # Call user group
        create_user_device_default_group(organization_id=org.id, owner_id=owner_id)

        return LambdaResponse(
            statusCode=201,
            body=DataNoList(data=parse_obj_as(ResponseModel, org)).json(by_alias=True),
        ).dict()
    except SQLAlchemyError as e:
        logger.error(e)
        connection.rollback()
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()
