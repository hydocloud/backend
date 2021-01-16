import logging
import boto3
from Crypto.Hash import HMAC, SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from typing import Optional
from os import environ
from botocore.exceptions import ClientError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from models.devices import Devices


logger = logging.getLogger(__name__)


class DeviceClass:
    def __init__(self, device_id: int):
        self.device_id = device_id

    def get_device(self, connection: Session) -> Optional[Devices]:
        try:
            res = connection.query(Devices).filter_by(id=self.device_id).first()
            return res
        except SQLAlchemyError as err:
            logger.error(err)
        return None

    def get_hmac(self, key: bytes, connection: Session) -> Optional[Devices]:
        try:
            res = connection.query(Devices.id, Devices.hmac_key).filter_by(
                id=self.device_id
            ).first()
            iv = res.hmac_key[:AES.block_size]
            cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
            self.hmac_key = unpad(cipher.decrypt(res.hmac_key[AES.block_size:]), AES.block_size)

        except SQLAlchemyError as err:
            logger.error(err)
        return None

    def digest(self, message: str) -> str:
        h = HMAC.new(self.hmac_key, digestmod=SHA256)
        h.update(message.encode())
        return h.hexdigest()

    def get_secret_key(self, secret_manager=None) -> bytes:
        secret_name = environ["SECRET_NAME"]
        if secret_manager is None:
            session = boto3.session.Session()
            secret_manager = session.client(service_name="secretsmanager")

        try:
            get_secret_value_response = secret_manager.get_secret_value(
                SecretId=secret_name
            )
            return get_secret_value_response["SecretString"].encode()
        except ClientError as err:
            logger.error(err)
            raise err
