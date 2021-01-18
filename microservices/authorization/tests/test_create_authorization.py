import pytest
import uuid
import json
from datetime import datetime
from create_authorization.create import create_authorization
from create_authorization.app import parse_input
from create_authorization import app
from models.authorization import AuthorizationModelApiInput


@pytest.fixture()
def authorization_input():
    return AuthorizationModelApiInput(
        userId=uuid.uuid4().__str__(),
        deviceId=1,
        accessLimit=1,
        endTime=datetime.utcnow(),
    )


@pytest.fixture
def sqs_event(authorization_input):
    """ Generate SQS event """
    return {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": authorization_input.json(),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001",
                },
                "messageAttributes": {},
                "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:create-device-group",
                "awsRegion": "eu-west-1",
            }
        ]
    }


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
        "pathParameters": {"proxy": "/path/to/resource"},
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


def test_create_authorization_ok(session, authorization_input):
    print(authorization_input)
    res = create_authorization(authorization_input, session)

    assert res["statusCode"] == 201


def test_create_authorization_wrong_input(session, authorization_input):
    authorization_input.__delattr__("deviceId")
    res = create_authorization(authorization_input, session)

    assert res["statusCode"] == 400


def test_parse_input_sqs_ok(sqs_event):
    res = parse_input(sqs_event)

    assert res is not None
    assert type(res) == AuthorizationModelApiInput


def test_parse_input_sqs_wrong(sqs_event):
    sqs_event["Records"][0]["body"] = json.dumps({"test": "test"})
    res = parse_input(sqs_event)

    assert res is None


def test_parse_input_apigw_ok(apigw_event):
    res = parse_input(apigw_event)

    assert res is not None
    assert type(res) == AuthorizationModelApiInput


def test_parse_input_apigw_wrong(apigw_event):
    apigw_event["body"] = json.dumps({"test": "test"})
    res = parse_input(apigw_event)

    assert res is None


def test_handler_payload_apigw(session, apigw_event):
    app.CONNECTION = session
    res = app.lambda_handler(apigw_event, None)

    assert res["statusCode"] == 201


def test_handler_payload_sqs(session, sqs_event):
    app.CONNECTION = session
    res = app.lambda_handler(sqs_event, None)

    assert res["statusCode"] == 201


def test_handler_payload_none(session, apigw_event):
    app.CONNECTION = session
    apigw_event["body"] = json.dumps({"test": "test"})
    res = app.lambda_handler(apigw_event, None)
    assert res is None
