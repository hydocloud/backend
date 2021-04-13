import pytest
import json
from get_organizations.get import get_organizations
from get_organizations import app


@pytest.fixture
def apigw_event(setup_org_id):
    """ Generate SQS event """
    return {
        "body": "",
        "resource": "/{proxy+}",
        "path": "/path/to/resource",
        "httpMethod": "POST",
        "isBase64Encoded": True,
        "multiValueQueryStringParameters": {"foo": ["bar"]},
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
            "authorizer": {"lambda": {"sub": setup_org_id.owner_id}},
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


def test_get_ok(session, setup_org_id):
    res = get_organizations(connection=session, owner_id=setup_org_id.owner_id)
    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert body["data"][0]["licenseId"] == setup_org_id.license_id
    assert body["data"][0]["name"] == setup_org_id.name
    assert body["data"][0]["ownerId"] == setup_org_id.owner_id.__str__()


def test_handler(session, setup_org_id, apigw_event):
    app.CONNECTION = session
    res = app.lambda_handler(apigw_event, None)
    body = json.loads(res["body"])

    assert res["statusCode"] == 200
    assert body["data"][0]["licenseId"] == setup_org_id.license_id
    assert body["data"][0]["name"] == setup_org_id.name
    assert body["data"][0]["ownerId"] == setup_org_id.owner_id.__str__()


def test_handler_multiple_org(session, setup_organizations, apigw_event):
    app.CONNECTION = session
    apigw_event["requestContext"]["authorizer"]["lambda"]["sub"] = setup_organizations[
        0
    ].owner_id
    res = app.lambda_handler(apigw_event, None)
    body = json.loads(res["body"])

    assert res["statusCode"] == 200
    assert len(body["data"]) == len(setup_organizations)
    assert body["data"][0]["licenseId"] == setup_organizations[0].license_id
    assert body["data"][0]["name"] == setup_organizations[0].name
    assert body["data"][0]["ownerId"] == setup_organizations[0].owner_id.__str__()


def test_handler_multiple_page(session, setup_organizations, apigw_event):
    app.CONNECTION = session
    apigw_event["requestContext"]["authorizer"]["lambda"]["sub"] = setup_organizations[
        0
    ].owner_id
    apigw_event["queryStringParameters"] = {"pageSize": 2}
    res = app.lambda_handler(apigw_event, None)
    body = json.loads(res["body"])

    assert res["statusCode"] == 200
    assert len(body["data"]) == 2
    assert body["total"] == len(setup_organizations)
    assert body["nextPage"] == 2
    assert body["previousPage"] == None
    assert body["totalPages"] == 2
    assert body["data"][0]["licenseId"] == setup_organizations[0].license_id
    assert body["data"][0]["name"] == setup_organizations[0].name
    assert body["data"][0]["ownerId"] == setup_organizations[0].owner_id.__str__()
