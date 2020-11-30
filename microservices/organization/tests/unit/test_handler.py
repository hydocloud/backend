import json

import pytest, os

from create_organization import app  


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "body":  '{\"name\": \"hello\", \"licenseId\": 1 }',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/examplepath",
    }

@pytest.fixture()
def mock_env_database(monkeypatch):    
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_HOST", "MacBook-Pro-di-Riccardo.local")
    monkeypatch.setenv("DB_NAME", "organizations")
    monkeypatch.setenv("DB_ENGINE", "postgresql")
    monkeypatch.setenv("DB_USER", "organization")
    monkeypatch.setenv("DB_PASSWORD", "organization")

def test_wrong_payload(mock_env_database):

    request = {
        "body":  '{\"name\": \"hello\"}'
    }

    ret = app.handler(request, "")
    payload = ret["body"]
    assert ret["statusCode"] == 400
    assert  "message" in ret["body"]

def test_lambda_handler(apigw_event, mock_env_database):

    ret = app.handler(apigw_event, "")
    payload = ret["body"]
    assert ret["statusCode"] == 201
    assert len(payload["data"]) == 1