import logging
import boto3
import json
from os import environ
from botocore.exceptions import ClientError
from pydantic import ValidationError
from indy import crypto, IndyError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from sqlalchemy import or_
from models.authorization import Unlock, Authorization
from models.wallet import Wallet


logger = logging.getLogger(__name__)


class AuthorizationClass:
    def __init__(self, obj: dict):
        try:
            self.unlock = Unlock.parse_obj(obj)
        except ValidationError as err:
            logger.error(err)

    def get_message(self, dynamodb=None):
        if dynamodb is None:
            dynamodb = boto3.resource("dynamodb")

        service_id = environ["SERVICE_ID"]
        if not dynamodb:
            dynamodb = boto3.resource(
                "dynamodb", endpoint_url=environ["DYNAMODB_ENDPOINT_OVERRIDE"]
            )

        table = dynamodb.Table(environ["NONCE_TABLE_NAME"])

        try:
            response = table.get_item(
                Key={"service_id": service_id, "message": self.unlock.message},
                ProjectionExpression="message",
            )
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
        else:
            try:
                self.service_message = response["Item"]["message"]
            except KeyError as e:
                logger.error(e)

    async def decrypt(self) -> bool:
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
        except IndyError as e:
            logger.error(e)
            return False

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
            return True
        except AssertionError as e:
            logger.error(e)
            return False

        return True

    def validation(self, user_id: str, connection: Session):
        """
        select
            a.id
        from
            authorizations a
        where
            (a.end_time is null or a.end_time > TO_TIMESTAMP( '2021-01-17 12:38:59', 'YYYY-MM-DD HH:MI:SS' ))
            and a.start_time <= TO_TIMESTAMP( '2021-01-17 12:38:59', 'YYYY-MM-DD HH:MI:SS' )
            and (a.access_limit is null or a.access_limit > 0)
        """
        try:
            item = (
                connection.query(Authorization.id, Authorization.access_time)
                .filter(
                    or_(
                        Authorization.end_time >= self.unlock.timestamp,
                        Authorization.end_time is None,
                    )
                )
                .filter(Authorization.start_time <= self.unlock.timestamp)
                .filter(
                    or_(
                        Authorization.access_time is None, Authorization.access_time > 0
                    )
                )
            )
            if item.access_time:
                item.access_limit = item.access_limit - 1
                connection.commit()
        except SQLAlchemyError as err:
            logger.error(err)
            connection.rollback()
