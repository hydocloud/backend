import sys

sys.path.append("./src/authorization_service")

from src.authorization_service.store_nonce import store


def test_store_nonce_ok(dynamodb, monkeypatch):
    monkeypatch.setenv("SERVICE_ID", "7bacf67c-4c3b-4e30-83fb-a96a93fd2c74")
    monkeypatch.setenv("NONCE_TABLE_NAME", "authorization_sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")
    message = "test"

    res = store(message, dynamodb)
    assert res is True


def test_store_nonce_ko(dynamodb, monkeypatch):
    monkeypatch.setenv("SERVICE_ID", "7bacf67c-4c3b-4e30-83fb-a96a93fd2c74")
    monkeypatch.setenv("NONCE_TABLE_NAME", "authorization_sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "sadsadasd")
    message = "test"

    res = store(message, dynamodb)
    assert res is False


def test_store_nonce_ko_with_no_dynamodb(dynamodb, monkeypatch):
    monkeypatch.setenv("SERVICE_ID", "7bacf67c-4c3b-4e30-83fb-a96a93fd2c74")
    monkeypatch.setenv("NONCE_TABLE_NAME", "authorization_sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "sadsadasd")
    message = "test"

    res = store(message, None)
    assert res is False
