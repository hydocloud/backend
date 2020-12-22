import json
import logging
from os import environ
from models.api import InputMessage  # type: ignore
from models.wallet import Wallet  # type: ignore
from pydantic import ValidationError
import boto3
from botocore.exceptions import ClientError
from compare_messages import (  # type: ignore
    get_message,
    decrypt,
    validate_data,
    update_session,
)
import asyncio

loop = asyncio.get_event_loop()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)
wallet_handle = None


def get_session(session_id, dynamodb=None):
    if dynamodb is None:
        dynamodb = boto3.resource("dynamodb")
    try:
        table_name = environ["SESSION_TABLE_NAME"]

        if environ["DYNAMODB_ENDPOINT_OVERRIDE"] != "":
            dynamodb = boto3.resource(
                "dynamodb", endpoint_url=environ["DYNAMODB_ENDPOINT_OVERRIDE"]
            )

        table = dynamodb.Table(table_name)

        response = table.get_item(Key={"id": session_id})
        return response["Item"]["status"]
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(e)
        if error_code == "ResourceNotFoundException":
            return 404
        return 500
    except AssertionError as e:
        logger.error(e)
        return 500
    except KeyError as e:
        logger.error(e)
        return 404


async def init_wallet():
    global wallet_handle

    if wallet_handle is None:
        x = Wallet()
        wallet_handle = await x.open_wallet()


def lambda_handler(event, context):
    logger.info("Open wallet")
    loop.run_until_complete(init_wallet())
    try:
        payload = json.loads(event["body"])
        InputMessage.parse_obj(payload)
    except ValidationError as e:
        logger.error(e)

    if get_session(payload["sessionId"]) != "PENDING":
        return {"statusCode": 400, "body": json.dumps({"success": False})}

    service_message = get_message(payload["message"])
    if not service_message:
        return {"statusCode": 409, "body": json.dumps({"success": False})}
    decrypted_user_message, decrypted_service_message = loop.run_until_complete(
        decrypt(payload["message"], service_message)
    )
    res, user_uuid = validate_data(
        json.loads(decrypted_user_message["message"]),
        json.loads(decrypted_service_message["message"]),
    )
    logger.info(res)
    if res:
        update_session(payload["sessionId"], user_uuid)
        return {"statusCode": 200, "body": json.dumps({"success": True})}

    return {"statusCode": 404, "body": json.dumps({"success": False})}
