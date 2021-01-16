import pytest
from datetime import datetime, timedelta
from faker import Faker
from models.authorization import Unlock
from models.devices import Devices, DevicesModel


faker = Faker()


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
    device = Devices(
        name=faker.sentence(nb_words=1),
        serial=faker.sentence(nb_words=1),
        device_group_id=1,
        hmac_key="ciaociaociaociaociaociaociaociao".encode(),
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

    def test_get_hmac(self, session, create_device):
        from validate_authorization.device import DeviceClass

        x = DeviceClass(create_device.id)
        res = x.get_hmac(connection=session)

        assert res.id == create_device.id
        assert res.hmac_key == create_device.hmac_key
        assert x.hmac_key == create_device.hmac_key

    def test_digest(self, create_device, session):
        from validate_authorization.device import DeviceClass

        x = DeviceClass(create_device.id)
        x.hmac_key = create_device.hmac_key
        res = x.digest(message="ciao")

        assert res == "d5cfd1d870147b8f1cbced82e601233e74b671710fcf83aef82d2cbd0e7f4675"
