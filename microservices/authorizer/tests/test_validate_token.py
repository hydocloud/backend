import json
import pytest
import jwt
import datetime
import sys, os, uuid
from app import validate_token

user_uuid = uuid.uuid4().__str__()


def test_validate_token(monkeypatch):
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
    res = validate_token(encoded_jwt)
    assert res["sub"] == user_uuid
    assert res["name"] == "authHydoLogin"


def test_validate_token_not_valid(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "secret")

    encoded_jwt = jwt.encode(
        {
            "name": "authHydoLogin",
            "sub": user_uuid,
            "exp": 100000000,
        },
        "secret",
        algorithm="HS256",
    ).decode()
    res = validate_token(encoded_jwt)
    assert res == False
