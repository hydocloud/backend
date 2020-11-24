import json
import uuid
import pytest
import boto3
import os, sys
sys.path.insert(0, os.path.abspath('.') + '/generate_jwt')
sys.path.insert(0, os.path.abspath('.') + '/generate_session')
from moto import mock_dynamodb2
from contextlib import contextmanager
from generate_jwt import app as generate_jwt_app
from generate_session import app as generate_session_app

class LambdaContext():
    def __init__(self):
        self.aws_request_id = uuid.uuid4()


context = LambdaContext()

@mock_dynamodb2
def test_store_session(monkeypatch):

    monkeypatch.setenv("SESSION_TABLE_NAME", "sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")
    dynamodb = boto3.resource('dynamodb', 'eu-west-1')
    dynamodb.create_table(
        TableName='sessions',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    session_id = context.aws_request_id.__str__()
    res = generate_session_app.store_session(session_id, dynamodb)
    assert res["ResponseMetadata"]["HTTPStatusCode"] == 200

@mock_dynamodb2
def test_store_get_session_pending(monkeypatch):

    monkeypatch.setenv("SESSION_TABLE_NAME", "sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")
    dynamodb = boto3.resource('dynamodb', 'eu-west-1')
    table = dynamodb.create_table(
        TableName='sessions',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    session_id = context.aws_request_id.__str__()
    table.put_item(Item={'id': session_id, 'status': 'PENDING', 'user_uuid': session_id})

    res, user_uuid = generate_jwt_app.get_session(session_id, dynamodb)
    assert res == 'PENDING'
    assert user_uuid == session_id

def test_store_get_session_not_found(monkeypatch):

    monkeypatch.setenv("SESSION_TABLE_NAME", "sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")
    dynamodb = boto3.resource('dynamodb', 'eu-west-1')
    session_id = context.aws_request_id.__str__()

    res = generate_jwt_app.get_session(session_id, dynamodb)
    assert res == 404

@mock_dynamodb2
def test_terminate_session_pending(monkeypatch):
    monkeypatch.setenv("SESSION_TABLE_NAME", "sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")

    session_id = context.aws_request_id.__str__()

    dynamodb = boto3.resource('dynamodb', 'eu-west-1')
    table = dynamodb.create_table(
        TableName='sessions',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    table.put_item(Item={'id': session_id, 'status': 'PENDING'})

    res = generate_jwt_app.terminate_session(session_id, dynamodb)
    assert res == 400

@mock_dynamodb2
def test_terminate_session_ok(monkeypatch):
    monkeypatch.setenv("SESSION_TABLE_NAME", "sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")

    session_id = context.aws_request_id.__str__()

    dynamodb = boto3.resource('dynamodb', 'eu-west-1')
    table = dynamodb.create_table(
        TableName='sessions',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    table.put_item(Item={'id': session_id, 'status': 'OK'})

    res = generate_jwt_app.terminate_session(session_id, dynamodb)
    assert res == 200

@mock_dynamodb2
def test_terminate_session_not_exist(monkeypatch):
    monkeypatch.setenv("SESSION_TABLE_NAME", "sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")

    dynamodb = boto3.resource('dynamodb', 'eu-west-1')
    table = dynamodb.create_table(
        TableName='sessions',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    session_id = 'asdsa'
    res = generate_jwt_app.terminate_session(session_id, dynamodb)
    assert res == 400

def test_terminate_session_wrong_setting(monkeypatch):
    monkeypatch.setenv("SESSION_TABLE_NAME", "sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")

    session_id = 'asdsa'
    res = generate_jwt_app.terminate_session(session_id)
    assert res == 400

# def test_terminate_session_dynamodb_setting(monkeypatch):
#     monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "http://localhost:8000")
#     monkeypatch.setenv("SESSION_TABLE_NAME", "sessions")

#     session_id = 'asdsa'
#     res = generate_jwt_app.terminate_session(session_id)
#     assert res == 400
