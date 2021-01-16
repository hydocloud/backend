import pytest
import boto3
from datetime import datetime, timedelta
from faker import Faker
from moto import mock_secretsmanager
from models.authorization import Unlock
from models.devices import Devices
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes


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
        deviceId=faker.random_int(),
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
def create_device(session):
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key=b"ciaociaociaociaociaociaociaociao", mode=AES.MODE_CBC, iv=iv)
    data = b"ciaociao"
    device = Devices(
        name=faker.sentence(nb_words=1),
        serial=faker.sentence(nb_words=1),
        device_group_id=1,
        hmac_key=(iv + cipher.encrypt(pad(data, AES.block_size))),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


def test_authorization_validation_ok(unlock):
    from validate_authorization.authorization import AuthorizationClass

    x = AuthorizationClass(unlock)
    assert x.unlock.deviceId == unlock["deviceId"]
    assert x.unlock.message == unlock["message"]
    assert x.unlock.deviceNonce == unlock["deviceNonce"]


def test_authorization_validation_ko(unlock):
    from validate_authorization.authorization import AuthorizationClass

    del unlock["deviceId"]
    x = AuthorizationClass(unlock)
    assert hasattr(x, "unlock") is False


def test_authorization_get_message(unlock, dynamodb, create_nonce, monkeypatch):
    from validate_authorization.authorization import AuthorizationClass

    monkeypatch.setenv("SERVICE_ID", "7bacf67c-4c3b-4e30-83fb-a96a93fd2c74")
    monkeypatch.setenv("NONCE_TABLE_NAME", "authorization_sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")

    x = AuthorizationClass(unlock)
    x.get_message(dynamodb=dynamodb)

    assert x.service_message == "test"


class TestDeviceClass:
    def test_device_init(self):
        from validate_authorization.device import DeviceClass

        x = DeviceClass(100)
        assert x.device_id == 100

    def test_get_device(self, session, create_device):
        from validate_authorization.device import DeviceClass

        x = DeviceClass(create_device.id)
        res = x.get_device(connection=session)

        assert res.id == create_device.id

    def test_get_hmac(self, session, create_device, monkeypatch):
        from validate_authorization.device import DeviceClass

        monkeypatch.setenv("SECRET_NAME", "DeviceSecret")

        x = DeviceClass(create_device.id)
        x.get_hmac(connection=session, key=b"ciaociaociaociaociaociaociaociao")

        assert x.hmac_key == "ciaociao".encode("utf-8")

    def test_digest(self, create_device, session):
        from validate_authorization.device import DeviceClass

        x = DeviceClass(create_device.id)
        x.hmac_key = b"ciaociaociaociaociaociaociaociao"
        res = x.digest(message="ciao")

        assert res == "d5cfd1d870147b8f1cbced82e601233e74b671710fcf83aef82d2cbd0e7f4675"

    def test_crypt_get_secret_ok(self, create_device, secret, monkeypatch):
        from validate_authorization.device import DeviceClass
        monkeypatch.setenv("SECRET_NAME", "java-util-test-password")

        x = DeviceClass(create_device.id)
        res = x.get_secret_key()

        assert type(res) == bytes
        assert res.decode() == "ciaociaociaociaociaociaociaociao"
    