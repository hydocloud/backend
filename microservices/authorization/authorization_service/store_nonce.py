import logging
from os import environ
import boto3
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def store(message: str, dynamodb=None) -> bool:
    if dynamodb is None:
        dynamodb = boto3.resource("dynamodb")
    try:
        table_name = environ["NONCE_TABLE_NAME"]

        if environ["DYNAMODB_ENDPOINT_OVERRIDE"] != "":
            dynamodb = boto3.resource(
                "dynamodb", endpoint_url=environ["DYNAMODB_ENDPOINT_OVERRIDE"]
            )

        table = dynamodb.Table(table_name)

        response = table.put_item(
            TableName=table_name,
            Item={
                "message": message,
                "service_id": environ["SERVICE_ID"],
                "expiration_time": int(
                    (datetime.utcnow() + timedelta(minutes=2)).timestamp()
                ),
            },
        )
        logger.info(response)
        return True
    except Exception as err:
        logger.error(err)
        return False
