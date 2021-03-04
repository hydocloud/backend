import json
import logging
import jwt
import datetime
import boto3
from botocore.exceptions import ClientError
from os import environ

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

dynamodb = boto3.resource("dynamodb")


def remove_prefix(text: str, prefix: str) -> str:
    """Remove prefix from string"""
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text  # or whatever


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
        logger.info(response)
        if "user_uuid" in response["Item"]:
            return response["Item"]["status"], response["Item"]["user_uuid"]
        else:
            return response["Item"]["status"], None
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(e)
        if error_code == "ResourceNotFoundException":
            return 404, None
        return 500, None
    except AssertionError as e:
        logger.error(e)
        return 500, None
    except KeyError as e:
        logger.error(e)
        return 404, None


def terminate_session(session_id, dynamodb=None):
    if dynamodb is None:
        dynamodb = boto3.resource("dynamodb")
    try:
        table_name = environ["SESSION_TABLE_NAME"]
        status = "DONE"

        if environ["DYNAMODB_ENDPOINT_OVERRIDE"] != "":
            dynamodb = boto3.resource(
                "dynamodb", endpoint_url=environ["DYNAMODB_ENDPOINT_OVERRIDE"]
            )

        table = dynamodb.Table(table_name)

        response = table.update_item(
            Key={"id": session_id},
            ConditionExpression="#st=:ok",
            UpdateExpression="set #st=:s",
            ExpressionAttributeValues={":s": status, ":ok": "OK"},
            ExpressionAttributeNames={"#st": "status"},
            ReturnValues="UPDATED_NEW",
        )
        logger.info(response)
        return 200
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(e)
        if error_code == "ConditionalCheckFailedException":
            return 400
        elif error_code == "ResourceNotFoundException":
            return 404
        return 500
    except AttributeError as e:
        logger.error(e)
        return 500


def validate_polling_jwt(polling_jwt, session_id):
    try:
        res = jwt.decode(polling_jwt, environ["JWT_SECRET"], algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        logger.error("Failed decode jwt")
        return False
    if res["sub"] == session_id:
        return True
    return False


def generate_jwt(user_uuid: str) -> str:
    logger.debug("Generate auth token")
    secret = environ["JWT_SECRET"]
    encoded_jwt = jwt.encode(
        {
            "name": "authHydoLogin",
            "sub": user_uuid,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
        },
        secret,
        algorithm="HS256",
    )
    return encoded_jwt


def lambda_handler(event, context):
    session_id = event["pathParameters"]["id"]
    polling_jwt = remove_prefix(event["headers"]["authorization"], "Bearer ")
    res = validate_polling_jwt(polling_jwt, session_id)
    if res is True:
        session_status, user_uuid = get_session(session_id)
        if session_status == "PENDING":
            return {"statusCode": 202, "body": json.dumps({"message": "Accepted"})}
        res_status_code = terminate_session(session_id)
        if res_status_code == 200:
            jwt = generate_jwt(user_uuid)
            return {"statusCode": res_status_code, "body": json.dumps({"jwt": jwt})}
        elif res_status_code == 404:
            return {
                "statusCode": res_status_code,
                "body": json.dumps({"message": "Not found"}),
            }
        elif res_status_code == 400:
            return {"statusCode": 409, "body": json.dumps({"message": "Conflict"})}
        else:
            return {
                "statusCode": res_status_code,
                "body": json.dumps({"message": "Internal server error"}),
            }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"}),
        }
