import json
import sys

import pytest

sys.path.append("./src/get_authorizations")
from faker import Faker
from models.authorization import Authorization
from sqlalchemy.orm.query import Query

from src.get_authorizations import app
from src.get_authorizations.app import lambda_handler
from src.get_authorizations.authorization_filter import AuthorizationFilter
from src.get_authorizations.get import get_authorizations

faker = Faker()


@pytest.fixture
def apigw_event():
    """ Generate API event """
    return {
        "body": None,
        "resource": "/{proxy+}",
        "path": "/path/to/resource",
        "httpMethod": "POST",
        "isBase64Encoded": True,
        "queryStringParameters": {"id": None},
        "multiValueQueryStringParameters": {"foo": ["bar"]},
        "pathParameters": {"id": None},
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


def test_class_authorization_filter_all(authorizations_session):
    x = AuthorizationFilter(
        query=authorizations_session.query(Authorization),
        user_id=faker.uuid4(),
        device_id=faker.random_int(),
        authorization_id=faker.random_int(),
    )
    res = x.build_filter()

    assert (
        str(res.whereclause)
        == "authorizations.id = :id_1 AND authorizations.user_id = :user_id_1 AND authorizations.device_id = :device_id_1"
    )
    assert type(res) == Query


def test_class_authorization_filter_no_user_id(authorizations_session):
    x = AuthorizationFilter(
        query=authorizations_session.query(Authorization),
        device_id=faker.random_int(),
        authorization_id=faker.random_int(),
    )
    res = x.build_filter()

    assert (
        str(res.whereclause)
        == "authorizations.id = :id_1 AND authorizations.device_id = :device_id_1"
    )
    assert type(res) == Query


def test_class_authorization_filter_no_device_id(authorizations_session):
    x = AuthorizationFilter(
        query=authorizations_session.query(Authorization),
        user_id=faker.uuid4(),
        authorization_id=faker.random_int(),
    )
    res = x.build_filter()

    assert (
        str(res.whereclause)
        == "authorizations.id = :id_1 AND authorizations.user_id = :user_id_1"
    )
    assert type(res) == Query


def test_get_authorizations_single_id(authorizations_session, populate_db):
    res = get_authorizations(
        connection=authorizations_session, authorization_id=populate_db[0].id
    )
    body = json.loads(res["body"])

    assert res["statusCode"] == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == populate_db[0].id


def test_get_authorizations_single_id_not_found(authorizations_session, populate_db):
    res = get_authorizations(connection=authorizations_session, authorization_id=1000)
    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert len(body["data"]) == 0


def test_get_authorizations_single_id_not_found_wrong_page(
    authorizations_session, populate_db
):
    res = get_authorizations(
        connection=authorizations_session, authorization_id=1000, page_number=100
    )

    assert res["statusCode"] == 400


def test_lambda_handler_authorization_id(
    authorizations_session, populate_db, apigw_event
):
    app.CONNECTION = authorizations_session
    apigw_event["pathParameters"] = {"id": 1}
    res = lambda_handler(apigw_event, None)

    assert res["statusCode"] == 200


def test_lambda_handler_authorization_id_device_id(
    authorizations_session, populate_db, apigw_event
):
    app.CONNECTION = authorizations_session
    apigw_event["pathParameters"] = {"id": 1}
    apigw_event["queryStringParameters"] = {"deviceId": 1}
    res = lambda_handler(apigw_event, None)

    assert res["statusCode"] == 400


def test_lambda_handler_authorization_id_device_id_user_id(
    authorizations_session, populate_db, apigw_event
):
    app.CONNECTION = authorizations_session
    apigw_event["pathParameters"] = {"id": 1}
    apigw_event["queryStringParameters"] = {"deviceId": 1, "userId": faker.uuid4()}
    res = lambda_handler(apigw_event, None)

    assert res["statusCode"] == 400


def test_lambda_handler_device_id_user_id(
    authorizations_session, populate_db, apigw_event
):
    app.CONNECTION = authorizations_session
    apigw_event["pathParameters"] = {}
    apigw_event["queryStringParameters"] = {"deviceId": 1, "userId": faker.uuid4()}
    res = lambda_handler(apigw_event, None)
    body = json.loads(res["body"])

    assert res["statusCode"] == 200
    assert len(body["data"]) == 0


def test_lambda_handler_device_id(authorizations_session, populate_db, apigw_event):
    app.CONNECTION = authorizations_session
    apigw_event["pathParameters"] = {}
    apigw_event["queryStringParameters"] = {"deviceId": populate_db[0].device_id}
    res = lambda_handler(apigw_event, None)

    assert res["statusCode"] == 200


def test_lambda_handler_user_id(authorizations_session, populate_db, apigw_event):
    app.CONNECTION = authorizations_session
    apigw_event["pathParameters"] = {}
    apigw_event["queryStringParameters"] = {"userId": populate_db[0].user_id}
    res = lambda_handler(apigw_event, None)

    assert res["statusCode"] == 200


def test_lambda_handler_device_id_user_id_validation_error(
    authorizations_session, populate_db, apigw_event
):
    app.CONNECTION = authorizations_session
    apigw_event["pathParameters"] = {}
    apigw_event["queryStringParameters"] = {}
    res = lambda_handler(apigw_event, None)

    assert res["statusCode"] == 400
