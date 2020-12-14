import logging
import datetime
import os
import boto3
import json
from botocore.exceptions import ClientError
from models.organizations import Organization, OrganizationsList, ResponseModel
from models.api_response import (
    LambdaErrorResponse,
    LambdaSuccessResponse,
    Message,
    Data,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from aws_lambda_powertools import Tracer

tracer = Tracer(service="create_organization")

logger = logging.getLogger(__name__)
QUEUE_URL = os.environ["QUEUE_URL"] if "QUEUE_URL" in os.environ else None


def create_user_group(organization_id: int, owner_id: str, name: str = "DEFAULT"):
    sqs = boto3.client("sqs")
    message = json.dumps({
        "name": name,
        "organizationId": organization_id,
        "ownerId": owner_id
        }
    )
    try:
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))
    except ClientError as err:
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
        return LambdaErrorResponse(
            body=(Message(message="Bad request")), statusCode=400
        )

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
        create_user_group(organization_id=org.id, owner_id=owner_id)

        return LambdaSuccessResponse(
            statusCode=201,
            body=Data(
                data=OrganizationsList(
                    organizations=[
                        ResponseModel(
                            id=org.id,
                            ownerId=org.owner_id,
                            name=org.name,
                            licenseId=org.license_id,
                        )
                    ]
                )
            ),
        )
    except SQLAlchemyError as e:
        logger.error(e)
        connection.rollback()
        return LambdaErrorResponse(
            body=(Message(message="Bad request")), statusCode=500
        )
