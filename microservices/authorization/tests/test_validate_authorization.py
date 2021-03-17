import pytest
import boto3
import uuid
from datetime import datetime, timedelta
from faker import Faker
from moto import mock_secretsmanager
from models.authorization import Unlock
from models.devices import Devices
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from pydantic import ValidationError


faker = Faker()


@mock_secretsmanager
@pytest.fixture(scope="function")
def secret():
    with mock_secretsmanager():
        conn = boto3.client("secretsmanager", region_name="eu-west-1")
        conn.create_secret(
            Name="java-util-test-password",
            SecretString="ciaociaociaociaociaociaociaociao",
        )
        yield conn


@pytest.fixture
def unlock() -> dict:
    return Unlock(
        message="test",
        deviceSerial=uuid.uuid4().__str__(),
        deviceNonce=faker.sentence(nb_words=1),
    ).dict()


@pytest.fixture
def create_nonce(dynamodb):
    table = dynamodb.Table("authorization_sessions")
    table.put_item(
        TableName="authorization_sessions",
        Item={
            "message": "test",
            "service_id": "7bacf67c-4c3b-4e30-83fb-a96a93fd2c74",
            "expiration_time": int(
                (datetime.utcnow() + timedelta(minutes=2)).timestamp()
            ),
        },
    )


@pytest.fixture
def create_device(devices_session):
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key=b"ciaociaociaociaociaociaociaociao", mode=AES.MODE_CBC, iv=iv)
    data = "ciaociao"
    device = Devices(
        name=faker.sentence(nb_words=1),
        serial=uuid.uuid4().__str__(),
        device_group_id=1,
        hmac_key=(iv + cipher.encrypt(pad(data.encode("utf-8"), AES.block_size))),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    devices_session.add(device)
    devices_session.commit()
    devices_session.refresh(device)
    return device


def test_authorization_validation_ok(unlock, authorizations_session):
    from validate_authorization.authorization import AuthorizationClass

    x = AuthorizationClass(obj=unlock, connection=authorizations_session)
    assert x.unlock.deviceSerial == unlock["deviceSerial"]
    assert x.unlock.message == unlock["message"]
    assert x.unlock.deviceNonce == unlock["deviceNonce"]
    assert x.db_connection == authorizations_session


def test_authorization_validation_ko(unlock, authorizations_session):
    from validate_authorization.authorization import AuthorizationClass

    del unlock["deviceSerial"]
    with pytest.raises(ValidationError):
        assert AuthorizationClass(obj=unlock, connection=authorizations_session)


def test_authorization_get_message(
    unlock, dynamodb, create_nonce, monkeypatch, authorizations_session
):
    from validate_authorization.authorization import AuthorizationClass

    monkeypatch.setenv("SERVICE_ID", "7bacf67c-4c3b-4e30-83fb-a96a93fd2c74")
    monkeypatch.setenv("NONCE_TABLE_NAME", "authorization_sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")

    x = AuthorizationClass(obj=unlock, connection=authorizations_session)
    x.get_message(dynamodb=dynamodb)

    assert x.service_message == "test"


class TestDeviceClass:

    def test_get_device(self, create_device, devices_session):
        from validate_authorization.device import DeviceClass

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        res = x.get_device()

        assert res.id == create_device.id

    def test_get_hmac(self, devices_session, create_device, monkeypatch):
        from validate_authorization.device import DeviceClass

        monkeypatch.setenv("SECRET_NAME", "DeviceSecret")

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        x.get_hmac(key=b"ciaociaociaociaociaociaociaociao")

        assert x.hmac_key == "ciaociao".encode("utf-8")

    def test_digest(self, create_device, devices_session):
        from validate_authorization.device import DeviceClass

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        x.hmac_key = b"ciaociaociaociaociaociaociaociao"
        res = x.digest(message="ciao")

        assert res == "d5cfd1d870147b8f1cbced82e601233e74b671710fcf83aef82d2cbd0e7f4675"

    def test_crypt_get_secret_ok(self, create_device, secret, monkeypatch, devices_session):
        from validate_authorization.device import DeviceClass

        monkeypatch.setenv("SECRET_NAME", "java-util-test-password")

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        res = x.get_secret_key()

        assert type(res) == bytes
        assert res.decode() == "ciaociaociaociaociaociaociaociao"
