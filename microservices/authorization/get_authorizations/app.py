""" Entry point lambda"""

import logging
import json
from aws_lambda_powertools import Tracer
from get import get_authorizations
from database import init_db
from models.authorization import AuthorizationModelParameters
from pydantic import ValidationError

tracer = Tracer(service="get_authorizations")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
CONNECTION = None


@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context) -> dict:
    """
    Based on both path parameters or query parameters chose if
    device require info about one device group or multiple
    """

    global CONNECTION

    if CONNECTION is None:
        CONNECTION = init_db()

    if "pathParameters" in event and "id" in event["pathParameters"]:

        authorization_id = event["pathParameters"]["id"]
        event["queryStringParameters"]["authorizationId"] = authorization_id

        try:
            query_string_parameters = AuthorizationModelParameters.parse_obj(
                event["queryStringParameters"]
            )
        except ValidationError as err:
            logger.error(err)
            return {"statusCode": 400, "body": json.dumps({"message": "Bad request"})}

        response = get_authorizations(
            connection=CONNECTION,
            page_number=query_string_parameters.pageNumber,
            page_size=query_string_parameters.pageSize,
            authorization_id=authorization_id,
        )
    else:
        try:
            query_string_parameters = AuthorizationModelParameters.parse_obj(
                event["queryStringParameters"]
            )
        except ValidationError as err:
            logger.error(err)
            return {"statusCode": 400, "body": json.dumps({"message": "Bad request"})}

        response = get_authorizations(
            connection=CONNECTION,
            page_number=query_string_parameters.pageNumber,
            page_size=query_string_parameters.pageSize,
            device_id=query_string_parameters.deviceId,
            user_id=query_string_parameters.userId,
        )

    return response
