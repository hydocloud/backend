import json
import pytest
import jwt
import datetime
import sys, os, uuid
from app import lambda_handler

user_uuid = uuid.uuid4().__str__()


def test_lambda_handler_validate_token(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "secret")

    encoded_jwt = jwt.encode(
        {
            "name": "authHydoLogin",
            "sub": user_uuid,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
        },
        "secret",
        algorithm="HS256",
    ).decode()
    event = {
        "headers": {
            "token": encoded_jwt
        }
    }
    res = lambda_handler(event, None)

    assert res["context"]["sub"] == user_uuid
    assert res["isAuthorized"] == True


def test_lambda_handler_invalidate_token(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "secret")

    encoded_jwt = jwt.encode(
        {
            "name": "authHydoLogin",
            "sub": user_uuid,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
        },
        "secret2",
        algorithm="HS256",
    ).decode()
    event = {
        "headers": {
            "token": encoded_jwt
        }
    }
    res = lambda_handler(event, None)

    assert res["isAuthorized"] == False
