import logging
import json
from os import environ
import boto3
from botocore.exceptions import ClientError
from indy import crypto, IndyError
from models.wallet import Wallet

logger = logging.getLogger(__name__)


def get_message(message, dynamodb=None):
    if dynamodb is None:
        dynamodb = boto3.resource("dynamodb")

    service_id = environ["LOGIN_ID"]
    if not dynamodb:
        dynamodb = boto3.resource(
            "dynamodb", endpoint_url=environ["DYNAMODB_ENDPOINT_OVERRIDE"]
        )

    table = dynamodb.Table(environ["NONCE_TABLE_NAME"])

    try:
        response = table.get_item(
            Key={"service_id": service_id, "message": message},
            ProjectionExpression="message",
        )
    except ClientError as e:
        logger.error(e.response["Error"]["Message"])
    else:
        try:
            return response["Item"]["message"]
        except KeyError as e:
            logger.error(e)


async def decrypt(user_message, service_message):
    x = Wallet.get_instance()
    wallet_handle = x.get_wallet_handle()
    logger.info("Decrypt messages")
    try:
        decrypted_user_mesage = await crypto.unpack_message(
            wallet_handle, user_message.encode("utf-8")
        )
        decrypted_service_mesage = await crypto.unpack_message(
            wallet_handle, service_message.encode("utf-8")
        )
    except IndyError as e:
        logger.error(e)

    return (
        json.loads(decrypted_user_mesage.decode("utf-8")),
        json.loads(decrypted_service_mesage.decode("utf-8")),
    )


def validate_data(decrypted_user_mesage, decrypted_service_mesage):

    try:
        assert decrypted_user_mesage["uuid"] == decrypted_service_mesage["uuid"]
        assert decrypted_user_mesage["message"] == decrypted_service_mesage["message"]
        assert (
            decrypted_user_mesage["timestamp"] == decrypted_service_mesage["timestamp"]
        )
        return True, decrypted_user_mesage["uuid"]
    except AssertionError as e:
        logger.error(e)
        return False


def update_session(session_id, user_uuid, dynamodb=None):

    if dynamodb is None:
        dynamodb = boto3.resource("dynamodb")

    try:
        table_name = environ["SESSION_TABLE_NAME"]
        status = "OK"

        if environ["DYNAMODB_ENDPOINT_OVERRIDE"] != "":
            dynamodb = boto3.resource(
                "dynamodb", endpoint_url=environ["DYNAMODB_ENDPOINT_OVERRIDE"]
            )

        table = dynamodb.Table(table_name)

        response = table.update_item(
            Key={"id": session_id},
            UpdateExpression="set #st=:s, #u=:u",
            ExpressionAttributeValues={":s": status, ":u": user_uuid},
            ExpressionAttributeNames={"#st": "status", "#u": "user_uuid"},
            ReturnValues="UPDATED_NEW",
        )
        logger.info(response)
        return response
    except Exception as e:
        logger.error(e)
        return False


def delete_data(message, dynamodb=None):
    service_id = environ["LOGIN_ID"]
    if not dynamodb:
        dynamodb = boto3.resource(
            "dynamodb", endpoint_url=environ["DYNAMODB_ENDPOINT_OVERRIDE"]
        )

    table = dynamodb.Table(environ["NONCE_TABLE_NAME"])
    try:
        response = table.delete_item(
            Key={"service_id": service_id, "message": message},
        )
    except ClientError as e:
        logger.error(e)
    else:
        logger.info(response)
