import uuid
import boto3
import pytest
import sys
import json
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from faker import Faker
from models.authorization import Unlock
from models.devices import Devices, DeviceGroups
from moto import mock_secretsmanager
from pydantic import ValidationError
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

sys.path.append("./src/validate_authorization")

faker = Faker()
ASYMMETRIC_KEYS = {
    "publicKey": "3059301306072a8648ce3d020106082a8648ce3d030107034200041e077a3600ebf9492aa024540d4f5301c6c4eb6c7d8463ffe15ce40d04e0a7be15073b42797c7c18ae00a9915fc5c02c6c8a1e5c007e096065d0cb353fd35e62",
    "privateKey": "308187020100301306072a8648ce3d020106082a8648ce3d030107046d306b02010104208188efb1d5413d79242e84f14b263b9162dd52a8bd3f3d29604c5da3de412f18a144034200041e077a3600ebf9492aa024540d4f5301c6c4eb6c7d8463ffe15ce40d04e0a7be15073b42797c7c18ae00a9915fc5c02c6c8a1e5c007e096065d0cb353fd35e62",
}


@mock_secretsmanager
@pytest.fixture(scope="function")
def secret():
    with mock_secretsmanager():
        conn = boto3.client("secretsmanager", region_name="eu-west-1")
        conn.create_secret(
            Name="java-util-test-password",
            SecretString="ciaociaociaociaociaociaociaociao",
        )
        conn.create_secret(
            Name="asymmetric-secret",
            SecretString=json.dumps(ASYMMETRIC_KEYS),
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


@pytest.fixture(scope="function")
def setup_device_group_id(devices_session):

    device_groups = DeviceGroups(
        name="asd",
        organization_id=1,
        owner_id=uuid.uuid4().__str__(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    devices_session.add(device_groups)
    devices_session.commit()
    devices_session.refresh(device_groups)
    return device_groups.id


@pytest.fixture
def create_device(setup_device_group_id, devices_session):
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key=b"ciaociaociaociaociaociaociaociao", mode=AES.MODE_CBC, iv=iv)
    data = "ciaociao"
    device = Devices(
        name=faker.sentence(nb_words=1),
        serial=uuid.uuid4().__str__(),
        device_group_id=setup_device_group_id,
        hmac_key=(iv + cipher.encrypt(pad(data.encode("utf-8"), AES.block_size))),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    devices_session.add(device)
    devices_session.commit()
    devices_session.refresh(device)
    return device


def test_authorization_validation_ok(unlock, authorizations_session):
    from src.validate_authorization.authorization import AuthorizationClass

    x = AuthorizationClass(obj=unlock, connection=authorizations_session)
    assert x.unlock.deviceSerial == unlock["deviceSerial"]
    assert x.unlock.message == unlock["message"]
    assert x.unlock.deviceNonce == unlock["deviceNonce"]
    assert x.db_connection == authorizations_session


def test_authorization_validation_ko(unlock, authorizations_session):
    from src.validate_authorization.authorization import AuthorizationClass

    del unlock["deviceSerial"]
    with pytest.raises(ValidationError):
        assert AuthorizationClass(obj=unlock, connection=authorizations_session)


def test_authorization_get_message(
    unlock, dynamodb, create_nonce, monkeypatch, authorizations_session
):
    from src.validate_authorization.authorization import AuthorizationClass

    monkeypatch.setenv("SERVICE_ID", "7bacf67c-4c3b-4e30-83fb-a96a93fd2c74")
    monkeypatch.setenv("NONCE_TABLE_NAME", "authorization_sessions")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_OVERRIDE", "")

    x = AuthorizationClass(obj=unlock, connection=authorizations_session)
    x.get_message(dynamodb=dynamodb)

    assert x.service_message == "test"


# def test_authorization_get_message_local(
#     unlock, dynamodb, create_nonce, monkeypatch, authorizations_session
# ):
#     from src.validate_authorization.authorization import AuthorizationClass

#     monkeypatch.setenv("SERVICE_ID", "7bacf67c-4c3b-4e30-83fb-a96a93fd2c74")
#     monkeypatch.setenv("NONCE_TABLE_NAME", "authorization_sessions")
#     monkeypatch.setenv(
#         "DYNAMODB_ENDPOINT_OVERRIDE", "http://MacBook-Pro-di-Riccardo.local:8000"
#     )

#     x = AuthorizationClass(obj=unlock, connection=authorizations_session)
#     x.get_message(dynamodb=dynamodb)

#     assert x.service_message == "test"


class TestDeviceClass:
    def test_get_device(self, create_device, devices_session):
        from src.validate_authorization.device import DeviceClass

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        res = x.get_device()

        assert res.id == create_device.id

    def test_get_hmac(self, devices_session, create_device, monkeypatch):
        from src.validate_authorization.device import DeviceClass

        monkeypatch.setenv("SECRET_NAME", "DeviceSecret")

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        x.get_hmac(key=b"ciaociaociaociaociaociaociaociao")

        assert x.hmac_key == "ciaociao".encode("utf-8")

    def test_digest(self, create_device, devices_session):
        from src.validate_authorization.device import DeviceClass

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        x.hmac_key = b"0102030405060708010203040506070801020304050607080102030405060708"
        res = x.digest(message="SAG7KstDgi6PkXoE4ByID7PDuGxHuJdq3s80vbJNQZ4=")
        assert res == "JNiHGNjZqBpW7XsXJ6ptFFkUAFqiBttn2WMMFm4X7a8="

    def test_crypt_get_secret_ok(
        self, create_device, secret, monkeypatch, devices_session
    ):
        from src.validate_authorization.device import DeviceClass

        monkeypatch.setenv("SECRET_NAME", "java-util-test-password")

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        res = x.get_secret_key()

        assert type(res) == bytes
        assert res.decode() == "ciaociaociaociaociaociaociaociao"

    def test_get_asymmetric_secret(
        self, create_device, secret, monkeypatch, devices_session
    ):
        from src.validate_authorization.device import DeviceClass

        monkeypatch.setenv("SECRET_NAME", "asymmetric-secret")

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        private = x.get_asymmetric_secret_key()

        assert type(private) == str
        assert ASYMMETRIC_KEYS["privateKey"] == private

    def test_signature(self, create_device, devices_session):
        from src.validate_authorization.device import DeviceClass

        x = DeviceClass(device_serial=create_device.serial, connection=devices_session)
        x.private_key = ASYMMETRIC_KEYS["privateKey"]
        res = x.signature(message="SAG7KstDgi6PkXoE4ByID7PDuGxHuJdq3s80vbJNQZ4=")
        print(ASYMMETRIC_KEYS["publicKey"])
        original_public_key = serialization.load_der_public_key(
            data=bytes.fromhex(ASYMMETRIC_KEYS["publicKey"])
        )
        verify = original_public_key.verify(
            bytes.fromhex(res),
            b"SAG7KstDgi6PkXoE4ByID7PDuGxHuJdq3s80vbJNQZ4=",
            ec.ECDSA(hashes.SHA256()),
        )
        assert verify is None
