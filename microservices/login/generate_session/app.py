import json
import qrcode
import logging
import jwt
import datetime
import boto3
from os import environ
from datetime import timedelta


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

client = boto3.client("dynamodb")


def store_session(session_id, dynamodb=None):
    if dynamodb is None:
        dynamodb = boto3.resource("dynamodb")

    try:
        table_name = environ["SESSION_TABLE_NAME"]
        status = "PENDING"

        if environ["DYNAMODB_ENDPOINT_OVERRIDE"] != "":
            dynamodb = boto3.resource(
                "dynamodb", endpoint_url=environ["DYNAMODB_ENDPOINT_OVERRIDE"]
            )

        table = dynamodb.Table(table_name)

        response = table.put_item(
            TableName=table_name,
            Item={
                "id": session_id,
                "status": status,
                "expiration_time": int(
                    (datetime.utcnow() + timedelta(minutes=10)).timestamp()
                ),
            },
        )
        logger.info(response)
        return response
    except Exception as e:
        logger.error(e)
        return False


def make_qrcode(service_id, session_id):
    data = {"serviceId": service_id, "sessionId": session_id.__str__()}
    qr = qrcode.make(data)
    return qr


def polling_jwt(session_id):
    logger.debug("Generate polling token")
    secret = environ["JWT_SECRET"]
    encoded_jwt = jwt.encode(
        {
            "sub": session_id,
            "name": "HydoLogin",
            "exp": datetime.utcnow() + timedelta(seconds=180),
        },
        secret,
        algorithm="HS256",
    ).decode()
    return encoded_jwt


def lambda_handler(event, context):

    service_id = environ["LOGIN_ID"]
    session_id = context.aws_request_id
    res = store_session(session_id.__str__())
    if res is not False:

        jwt = polling_jwt(session_id)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"sessionId": str(session_id), "serviceId": str(service_id), "jwt": jwt}
            ),
        }

    return {
        "statusCode": 500,
        "body": json.dumps({"message": "Internal server errror"}),
    }
