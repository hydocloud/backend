import copy
import datetime
import json
import sys
import uuid

import pytest
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from models.devices import DeviceGroups, DevicesApiInput

sys.path.append("./src/create_device")
from src.create_device import app, create  # noqa: E402
from src.create_device.create import create_authorization, create_device  # noqa: E402


@pytest.fixture
def sqs_event():
    """ Generate SQS event """
    return {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": '{"deviceId": 2, "userId": "asdasd"}',
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
def apigw_event(device):
    """ Generate SQS event """
    return {
        "body": json.dumps(device.dict()),
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


@pytest.fixture(scope="function")
def setup_device_group_id(session):

    device_groups = DeviceGroups(
        name="asd",
        organization_id=1,
        owner_id=uuid.uuid4().__str__(),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    session.add(device_groups)
    session.commit()
    session.refresh(device_groups)
    return device_groups.id


@pytest.fixture
def device(setup_device_group_id):
    return DevicesApiInput(
        name="test",
        serial=uuid.uuid4().__str__(),
        deviceGroupId=setup_device_group_id,
        hmacKey="testest",
    )


def test_create_device_ok(device, session, secret, sqs_queue, monkeypatch):

    monkeypatch.setenv("SECRET_NAME", "java-util-test-password")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")

    user_id = "asddss"
    res = create_device(user_id=user_id, payload=device, connection=session)
    body = (json.loads(res["body"]))["data"]

    assert res["statusCode"] == 201
    assert body["serial"] == device.serial
    assert body["deviceGroupId"] == device.deviceGroupId
    assert body["name"] == device.name


def test_create_device_double(device, session, secret, sqs_queue, monkeypatch):

    monkeypatch.setenv("SECRET_NAME", "java-util-test-password")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    user_id = "asddss"

    res = create_device(user_id=user_id, payload=device, connection=session)
    res2 = create_device(user_id=user_id, payload=device, connection=session)
    assert res["statusCode"] == 201
    assert res2["statusCode"] == 409


def test_handler(apigw_event, session, secret, sqs_queue, monkeypatch):
    monkeypatch.setenv("SECRET_NAME", "java-util-test-password")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    app.CONNECTION = session
    res = app.lambda_handler(apigw_event, None)
    body = (json.loads(res["body"]))["data"]
    apigw_event_body = json.loads(apigw_event["body"])

    assert res["statusCode"] == 201
    assert body["serial"] == apigw_event_body["serial"]
    assert body["deviceGroupId"] == apigw_event_body["deviceGroupId"]
    assert body["name"] == apigw_event_body["name"]


def test_create_device_validation_error(device, session):
    user_id = "asddss"
    local_device = copy.deepcopy(device)
    local_device.__delattr__("serial")
    res = create_device(user_id=user_id, payload=local_device, connection=session)
    assert res["statusCode"] == 400


def test_create_device_sqlalchemy_error(device, session, secret, monkeypatch):
    monkeypatch.setenv("SECRET_NAME", "java-util-test-password")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    session.invalidate()
    user_id = "asddss"
    res = create_device(user_id=user_id, payload=device, connection=session)
    assert res["statusCode"] == 500


def test_crypt_get_secret_ok(secret, monkeypatch):
    monkeypatch.setenv("SECRET_NAME", "java-util-test-password")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    res = create.get_key(secret)

    assert type(res) == bytes
    assert res.decode() == "ciaociaociaociaociaociaociaociao"


def test_crypt_encrypt_ok(secret, monkeypatch):
    monkeypatch.setenv("SECRET_NAME", "java-util-test-password")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    data = "ciaociaociao"
    res = create.encrypt_data(data)

    cipher = AES.new(
        b"ciaociaociaociaociaociaociaociao", AES.MODE_CBC, res[: AES.block_size]
    )
    plaintext = unpad(cipher.decrypt(res[AES.block_size :]), AES.block_size)
    assert type(res) == bytes
    assert plaintext.decode() == data


def test_handler_error_payload(apigw_event, session, secret, sqs_queue, monkeypatch):
    app.CONNECTION = session
    apigw_event["body"] = json.dumps({"name": "test"})
    res = app.lambda_handler(apigw_event, None)

    assert res["statusCode"] == 400


def test_create_device_no_sqs():
    user_id = "asddss"
    with pytest.raises(Exception):
        create_authorization(device_id=1, user_id=user_id)
