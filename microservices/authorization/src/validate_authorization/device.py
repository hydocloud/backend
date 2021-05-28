import base64
import hmac
import logging
import json
from hashlib import sha256
from os import environ
from typing import Optional
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities import parameters
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from models.devices import Devices
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

tracer = Tracer(service="validate-authorization")
logger = logging.getLogger(__name__)


class DeviceClass:
    def __init__(self, device_serial: str, connection: Session):
        self.device_serial = device_serial
        self.db_connection = connection
        self.get_device()

    @tracer.capture_method
    def get_device(self) -> Optional[Devices]:
        try:
            res = (
                self.db_connection.query(Devices)
                .filter_by(serial=self.device_serial)
                .first()
            )
            self.device_id = res.id
            return res
        except SQLAlchemyError as err:
            logger.error(err)
        return None

    @tracer.capture_method
    def get_hmac(self, key: bytes) -> Optional[Devices]:
        try:
            res = (
                self.db_connection.query(Devices.serial, Devices.hmac_key)
                .filter_by(serial=self.device_serial)
                .first()
            )
            iv = res.hmac_key[: AES.block_size]
            cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
            self.hmac_key = unpad(
                cipher.decrypt(res.hmac_key[AES.block_size :]), AES.block_size
            )
            logger.debug(f"hmac_key: {self.hmac_key}")

        except SQLAlchemyError as err:
            logger.error(err)
        return None

    @tracer.capture_method
    def digest(self, message: str) -> str:
        signature = hmac.new(
            key=bytes.fromhex(self.hmac_key.decode()),
            msg=base64.b64decode(message),
            digestmod=sha256,
        ).digest()
        logger.debug(
            f"message: {message}, digest: {signature}, digest_base64: {base64.b64encode(signature)}"
        )
        return base64.b64encode(signature).decode()

    @tracer.capture_method
    def signature(self, message: str) -> str:
        private_key_from_hex = bytes.fromhex(self.private_key)
        original_private_key = serialization.load_der_private_key(
            data=private_key_from_hex, password=None
        )
        signature = original_private_key.sign(
            data=message.encode(), signature_algorithm=ec.ECDSA(hashes.SHA256())
        )
        return signature.hex()

    @tracer.capture_method
    def get_secret_key(self, secret_manager=None) -> bytes:
        try:
            secret = parameters.get_secret(environ["SECRET_NAME"])
            return secret.encode()
        except (
            parameters.GetParameterError,
            parameters.TransformParameterError,
        ) as err:
            logger.error(err)
            raise err

    @tracer.capture_method
    def get_asymmetric_secret_key(self, secret_manager=None) -> str:
        try:
            secret = parameters.get_secret(environ["SECRET_NAME"])
            secret = json.loads(secret)
            self.private_key = secret["privateKey"]
            return self.private_key
        except (
            parameters.GetParameterError,
            parameters.TransformParameterError,
        ) as err:
            logger.error(err)
            raise err
