import json
import pytest
import jwt
import datetime
import sys, os, uuid
sys.path.insert(0, os.path.abspath('.') + '/generate_jwt')
from generate_session import app
from generate_jwt.app import validate_polling_jwt, generate_jwt

session_id = uuid.uuid4().__str__()

def test_polling_jwt(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", 'secret')

    now = datetime.datetime.utcnow()
    encoded_jwt = app.polling_jwt(session_id)
    res = jwt.decode(encoded_jwt, 'secret', algorithms=['HS256'])
    assert res['sub'] == session_id
    assert res['name'] == 'HydoLogin'
    assert res['exp'] > int(now.timestamp())

def test_validate_polling_jwt_true(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", 'secret')
    encoded_jwt = app.polling_jwt(session_id)
    res = validate_polling_jwt(encoded_jwt, session_id)
    assert res == True

def test_validate_polling_jwt_false(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", 'secret')
    encoded_jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoeWRvTG9naW4iLCJleHAiOjE2MDE2NjY4MjF9.nIYY8oFDSBLxXNPIyZG6BR9ZgkLS_zZ7MLzN06JKCUs"
    res = validate_polling_jwt(encoded_jwt, session_id)
    assert res == False

def test_generate_jwt(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", 'secret')

    now = datetime.datetime.utcnow()
    encoded_jwt = generate_jwt()
    res = jwt.decode(encoded_jwt, 'secret', algorithms=['HS256'])
    assert res['sub'] == 'authHydoLogin'
    assert res['exp'] > int(now.timestamp())