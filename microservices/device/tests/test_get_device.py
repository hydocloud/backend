import pytest
import datetime
import json
import uuid
import sys
from models.devices import Devices

sys.path.append("./src/get_devices")
from src.get_devices.get import get_devices  # noqa: E402
from src.get_devices import app  # noqa: E402


@pytest.fixture
def apigw_event(devices):
    device1, _, _ = devices
    return {
        "resource": "/{proxy+}",
        "path": "/path/to/resource",
        "httpMethod": "POST",
        "isBase64Encoded": True,
        "queryStringParameters": {"deviceGroupId": device1.device_group_id},
        "multiValueQueryStringParameters": {"foo": ["bar"]},
        "pathParameters": {"id": device1.id},
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
def devices(setup_device_group_id, session):
    device = Devices(
        name="a",
        serial=uuid.uuid4().__str__(),
        device_group_id=setup_device_group_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    device2 = Devices(
        name="a",
        serial=uuid.uuid4().__str__(),
        device_group_id=setup_device_group_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    device3 = Devices(
        name="a",
        serial=uuid.uuid4().__str__(),
        device_group_id=setup_device_group_id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    devices = [device, device2, device3]
    session.bulk_save_objects(devices, return_defaults=True)
    return devices[0], devices[1], devices[2]


def test_get_device_ok(devices, session):
    device1, _, _ = devices
    res = get_devices(
        device_id=device1.id,
        device_group_id=device1.device_group_id,
        connection=session,
    )
    assert res["statusCode"] == 200


def test_get_devices_ok(devices, session):
    device1, device2, device3 = devices
    res = get_devices(device_group_id=device1.device_group_id, connection=session)
    devices_res = (json.loads(res["body"]))["data"]
    assert res["statusCode"] == 200
    assert len(devices_res) == 3


def test_get_devices_ok_page_size(devices, session):
    device1, device2, device3 = devices
    res = get_devices(
        device_group_id=device1.device_group_id, page_size=1, connection=session
    )
    body = json.loads(res["body"])
    devices_res = body["data"]
    assert res["statusCode"] == 200
    assert len(devices_res) == 1
    assert body["total"] == 3
    assert body["nextPage"] == 2


def test_get_devices_ok_page_size_next(devices, session):
    device1, device2, device3 = devices
    res = get_devices(
        device_group_id=device1.device_group_id,
        page_size=1,
        page_number=2,
        connection=session,
    )
    body = json.loads(res["body"])
    devices_res = body["data"]
    assert res["statusCode"] == 200
    assert len(devices_res) == 1
    assert body["total"] == 3
    assert body["nextPage"] == 3
    assert body["previousPage"] == 1


def test_edit_device_not_found(session):
    res = get_devices(device_id=0, connection=session)
    body = json.loads(res["body"])
    assert len(body["data"]) == 0
    assert res["statusCode"] == 200


def test_get_device_organizations_id(devices, session):
    device1, _, _ = devices
    res = get_devices(organization_id=1, connection=session)
    assert res["statusCode"] == 200


def test_handler_ok(apigw_event, session):
    app.CONNECTION = session
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 200


def test_handler_not_found(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"]["id"] = 0
    apigw_event["queryStringParameters"]["deviceGroupId"] = 1
    res = app.lambda_handler(apigw_event, None)
    body = json.loads(res["body"])
    assert len(body["data"]) == 0
    assert res["statusCode"] == 200


def test_handler_no_id(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"] = None
    apigw_event["queryStringParameters"]["deviceGroupId"] = 1
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 200


def test_handler_organizations_id_device_group_id(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"] = None
    apigw_event["queryStringParameters"]["organizationId"] = 1
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 400


def test_handler_ok_with_page_and_page_size(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"] = None
    apigw_event["queryStringParameters"]["pageSize"] = 2
    apigw_event["queryStringParameters"]["page"] = 1
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 200


def test_handler_ok_with_page_size(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"] = None
    apigw_event["queryStringParameters"]["pageSize"] = 2
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 200


def test_handler_ok_with_wrong_page(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"] = None
    apigw_event["queryStringParameters"]["page"] = 2
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 200


def test_handler_ok_with_page(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"] = None
    apigw_event["queryStringParameters"]["page"] = 1
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 200


def test_get_device_invalidate_session(devices, session):
    session.invalidate()
    res = get_devices(device_id=1, connection=session)
    assert res["statusCode"] == 500


def test_handler_a(apigw_event, session):
    app.CONNECTION = session
    apigw_event["pathParameters"] = None
    apigw_event["queryStringParameters"]["deviceGroupId"] = None
    apigw_event["queryStringParameters"]["organizationId"] = 1
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 200


def test_handler_emanuele(apigw_event, session):
    app.CONNECTION = session
    del apigw_event["pathParameters"]
    apigw_event["queryStringParameters"]["page"] = 1
    apigw_event["queryStringParameters"]["pageSize"] = 10
    apigw_event["queryStringParameters"]["organizationId"] = 1
    del apigw_event["queryStringParameters"]["deviceGroupId"]
    res = app.lambda_handler(apigw_event, None)
    assert res["statusCode"] == 200
