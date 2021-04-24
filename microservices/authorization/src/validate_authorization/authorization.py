import json
import logging
from os import environ
from typing import Optional, Tuple

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities import parameters
from botocore.exceptions import ClientError
from device import DeviceClass
from indy import IndyError, crypto
from models.authorization import Authorization, Unlock
from models.wallet import Wallet
from pydantic import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

tracer = Tracer(service="validate-authorization")
logger = logging.getLogger(__name__)


class AuthorizationClass:
    def __init__(self, obj: dict, connection: Session):
        try:
            self.unlock = Unlock.parse_obj(obj)
            self.db_connection = connection
            logger.debug(f"Unlock: {self.unlock }")
        except ValidationError as err:
            logger.error(err)
            raise ValidationError(errors="Validation error", model=Unlock)

    @tracer.capture_method
    def get_message(self, dynamodb=None):
        service_id = environ["SERVICE_ID"]

        dynamodb_provider = parameters.DynamoDBProvider(
            table_name=environ["NONCE_TABLE_NAME"],
            key_attr="service_id",
            sort_attr="message",
            value_attr="message",
        )

        if environ["DYNAMODB_ENDPOINT_OVERRIDE"] != "":
            dynamodb_provider = parameters.DynamoDBProvider(
                table_name=environ["NONCE_TABLE_NAME"],
                key_attr="service_id",
                sort_attr="message",
                value_attr="message",
            )

        try:
            res = dynamodb_provider.get_multiple(service_id)
            logger.debug(f"Responses: \n{res}")
            for k, v in res.items():
                if v == self.unlock.message:
                    logger.debug(f"Message {v}")
                    response = v
                    break
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
            raise ClientError
        else:
            try:
                self.service_message = response
            except KeyError as e:
                logger.error(e)
                raise KeyError

    @tracer.capture_method
    async def decrypt(self) -> Tuple[bool, Optional[str]]:
        x = Wallet.get_instance()
        wallet_handle = x.get_wallet_handle()
        logger.info("Decrypt messages")
        try:
            self.decrypted_user_mesage = json.loads(
                await crypto.unpack_message(
                    wallet_handle, self.unlock.message.encode("utf-8")
                )
            )
            self.decrypted_service_mesage = json.loads(
                await crypto.unpack_message(
                    wallet_handle, self.service_message.encode("utf-8")
                )
            )
            self.decrypted_user_mesage = json.loads(
                self.decrypted_user_mesage["message"]
            )
            self.decrypted_service_mesage = json.loads(
                self.decrypted_service_mesage["message"]
            )
        except IndyError as e:
            logger.error(e)
            return False, None
        try:
            assert (
                self.decrypted_user_mesage["uuid"]
                == self.decrypted_service_mesage["uuid"]
            )
            assert (
                self.decrypted_user_mesage["message"]
                == self.decrypted_service_mesage["message"]
            )
            assert (
                self.decrypted_user_mesage["timestamp"]
                == self.decrypted_service_mesage["timestamp"]
            )
            return True, self.decrypted_user_mesage["uuid"]
        except AssertionError as e:
            logger.error(e)
            return False, None

        return False, None

    @tracer.capture_method
    def validation(
        self, user_id: str, device: DeviceClass, key: bytes
    ) -> Optional[str]:

        try:
            item = (
                self.db_connection.query(Authorization)
                .filter(
                    or_(
                        Authorization.end_time >= self.unlock.timestamp,
                        Authorization.end_time == None,
                    )
                )
                .filter(Authorization.start_time <= self.unlock.timestamp)
                .filter(
                    or_(
                        Authorization.access_limit == None,
                        Authorization.access_limit > 0,
                    )
                )
                .filter(Authorization.device_id == device.device_id)
                .filter(Authorization.user_id == user_id)
                .first()
            )
            logger.debug(f"ITEM: {item}")
            if item:
                device.get_hmac(key=key)
                digest = device.digest(self.unlock.deviceNonce)
                if item.access_limit:
                    item.access_limit = item.access_limit - 1
                    logger.debug(item.access_limit)
                    self.db_connection.commit()
                return digest
            else:
                return None

        except (SQLAlchemyError, Exception) as err:
            logger.error(err)
            self.db_connection.rollback()
            return None
