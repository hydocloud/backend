import json
import sys
import uuid

import pytest

sys.path.append("./src/edit_authorization")
from datetime import datetime

from models.authorization import AuthorizationModelApiInput

from src.edit_authorization import app
from src.edit_authorization.app import lambda_handler
from src.edit_authorization.edit import edit_authorization


@pytest.fixture()
def authorization_input():
    return AuthorizationModelApiInput(
        userId=uuid.uuid4().__str__(),
        deviceId=1,
        accessLimit=1,
        endTime=datetime.utcnow(),
    )


@pytest.fixture
def apigw_event(authorization_input):
    """ Generate SQS event """
    return {
        "body": authorization_input.json(),
        "resource": "/{proxy+}",
        "path": "/path/to/resource",
        "httpMethod": "POST",
        "isBase64Encoded": True,
        "queryStringParameters": {"foo": "bar"},
        "multiValueQueryStringParameters": {"foo": ["bar"]},
        "pathParameters": {"id": 1},
        "stageVariables": {"baz": "qux"},
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8",
            "Cache-Control": "max-age=0",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "US",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "Upgrade-Insecure-Requests": "1",
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
        },
        "multiValueHeaders": {
            "Accept": [
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            ],
            "Accept-Encoding": ["gzip, deflate, sdch"],
            "Accept-Language": ["en-US,en;q=0.8"],
            "Cache-Control": ["max-age=0"],
            "CloudFront-Forwarded-Proto": ["https"],
            "CloudFront-Is-Desktop-Viewer": ["true"],
            "CloudFront-Is-Mobile-Viewer": ["false"],
            "CloudFront-Is-SmartTV-Viewer": ["false"],
            "CloudFront-Is-Tablet-Viewer": ["false"],
            "CloudFront-Viewer-Country": ["US"],
            "Host": ["0123456789.execute-api.us-east-1.amazonaws.com"],
            "Upgrade-Insecure-Requests": ["1"],
            "User-Agent": ["Custom User Agent String"],
            "Via": ["1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)"],
            "X-Amz-Cf-Id": ["cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA=="],
            "X-Forwarded-For": ["127.0.0.1, 127.0.0.2"],
            "X-Forwarded-Port": ["443"],
            "X-Forwarded-Proto": ["https"],
        },
        "requestContext": {
            "authorizer": {"lambda": {"sub": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef"}},
            "accountId": "123456789012",
            "resourceId": "123456",
            "stage": "prod",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "requestTime": "09/Apr/2015:12:34:56 +0000",
            "requestTimeEpoch": 1428582896000,
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "accessKey": None,
                "sourceIp": "127.0.0.1",
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "Custom User Agent String",
                "user": None,
            },
            "path": "/prod/path/to/resource",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "apiId": "1234567890",
            "protocol": "HTTP/1.1",
        },
    }


def test_edit_authorization_ok(
    authorizations_session, populate_db, authorization_input
):
    res = edit_authorization(
        authorization_id=populate_db[0].id,
        payload=authorization_input,
        connection=authorizations_session,
    )
    body = json.loads(res["body"])

    assert res["statusCode"] == 201
    assert body["data"]["id"] == populate_db[0].id
    assert body["data"]["userId"] == authorization_input.userId.__str__()
    assert body["data"]["deviceId"] == authorization_input.deviceId
    assert body["data"]["accessLimit"] == authorization_input.accessLimit
    assert body["data"]["startTime"] == authorization_input.startTime.isoformat()
    assert body["data"]["endTime"] == authorization_input.endTime.isoformat()


def test_edit_authorization_not_found(
    authorizations_session, populate_db, authorization_input
):
    authorization_input.__delattr__("deviceId")
    res = edit_authorization(
        authorization_id=100,
        payload=authorization_input,
        connection=authorizations_session,
    )

    assert res["statusCode"] == 404


def test_edit_authorization_error(
    authorizations_session, populate_db, authorization_input
):
    res = edit_authorization(
        authorization_id=100,
        payload=authorization_input,
        connection=authorizations_session.close(),
    )

    assert res["statusCode"] == 500


def test_lambda_handler_ok(
    authorizations_session, populate_db, apigw_event, authorization_input
):
    app.CONNECTION = authorizations_session

    apigw_event["body"] = authorization_input.json()
    apigw_event["pathParameters"] = {"id": populate_db[0].id}
    res = lambda_handler(apigw_event, None)
    body = json.loads(res["body"])

    assert res["statusCode"] == 201
    assert body["data"]["id"] == populate_db[0].id
    assert body["data"]["userId"] == authorization_input.userId.__str__()
    assert body["data"]["deviceId"] == authorization_input.deviceId
    assert body["data"]["accessLimit"] == authorization_input.accessLimit
    assert body["data"]["startTime"] == authorization_input.startTime.isoformat()
    assert body["data"]["endTime"] == authorization_input.endTime.isoformat()


def test_lambda_handler_bad_request(
    authorizations_session, populate_db, apigw_event, authorization_input
):
    app.CONNECTION = authorizations_session
    apigw_event["body"] = json.dumps({"test": "asds"})
    res = lambda_handler(apigw_event, None)

    assert res["statusCode"] == 400
