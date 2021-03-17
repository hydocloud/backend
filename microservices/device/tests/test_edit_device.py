import pytest
import datetime
import json
import uuid
from edit_device.edit import edit_device
from edit_device import app
from models.devices import Devices, DevicesEditInput, DeviceGroups


@pytest.fixture(scope="function")
def new_group_id(session):

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
def apigw_event(device, device_edit):
    return {
        "body": json.dumps(device_edit.dict()),
        "resource": "/{proxy+}",
        "path": "/path/to/resource",
        "httpMethod": "POST",
        "isBase64Encoded": True,
        "queryStringParameters": {"foo": "bar"},
        "multiValueQueryStringParameters": {"foo": ["bar"]},
        "pathParameters": {"id": device.id},
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


@pytest.fixture
def device_edit(new_group_id, session):
    return DevicesEditInput(name="asdsa", deviceGroupId=new_group_id)


@pytest.fixture
def device(setup_device_group_id, session):
    device = Devices(
        serial=uuid.uuid4().__str__(),
        device_group_id=setup_device_group_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


def test_edit_device_ok(device, device_edit, session):
    res = edit_device(device_id=device.id, payload=device_edit, connection=session)
    assert res["statusCode"] == 201


def test_edit_device_not_found(device_edit, session):
    res = edit_device(device_id=0, payload=device_edit, connection=session)
    assert res["statusCode"] == 404


def test_handler_ok(apigw_event, session):
    app.CONNECTION = session
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 201


def test_handler_not_found(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"]["id"] = 0
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 404


def test_handler_bad_input_no_json(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"]["id"] = 0
    apigw_event["body"] = "asds"
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 400


def test_handler_bad_input_json(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"]["id"] = 0
    apigw_event["body"] = '{"test":"asdsa}'
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 400


def test_handler_no_connection(apigw_event, monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_database")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "ciaociao")
    monkeypatch.setenv("DB_ENGINE", "postgresql")
    app.CONNECTION = None
    apigw_event["pathParameters"]["id"] = 0
    apigw_event["body"] = '{"test":"asdsa}'
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 400


def test_edit_device_invalidate_session(device_edit, session):
    session.invalidate()
    res = edit_device(device_id=0, payload=device_edit, connection=session)
    assert res["statusCode"] == 500
