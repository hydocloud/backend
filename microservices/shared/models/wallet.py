import json
import logging
import os
import sys
from ctypes import CDLL, c_char_p

from indy import wallet  # type: ignore
from indy.error import ErrorCode, IndyError  # type: ignore

logger = logging.getLogger(__name__)

db_port = os.environ["DB_INDY_PORT"]
db_host = os.environ["DB_INDY_HOST"]
db_name = os.environ["DB_INDY_NAME"]
db_user = os.environ["DB_INDY_USER"]
db_password = os.environ["DB_INDY_PASSWORD"]


class Wallet(object):

    __instance = None

    @staticmethod
    def get_instance():
        if Wallet.__instance is None:
            Wallet()
        return Wallet.__instance

    def __init__(self):
        if Wallet.__instance is not None:
            return Wallet.__instance
        else:
            Wallet.__instance = self
            self.name = os.environ["DB_INDY_SERVICE_NAME"]
            self.key = os.environ["DB_INDY_SERVICE_PASSWORD"]
            self.name_json = json.dumps(
                {
                    "id": self.name,
                    "storage_type": "postgres_storage",
                    "storage_config": {
                        "url": "{}:{}".format(db_host, db_port),
                        "wallet_scheme": "MultiWalletSingleTable",
                    },
                }
            )
            self.key_json = json.dumps(
                {
                    "key": self.key,
                    "storage_credentials": {
                        "account": db_user,
                        "password": db_password,
                        "admin_account": db_user,
                        "admin_password": db_password,
                    },
                }
            )
            
            stg_lib = CDLL("/opt/lib/libindystrgpostgres.so")
            result = stg_lib["postgresstorage_init"]()
            if result != 0:
                logger.error("Error unable to load wallet storage {}".format(result))
                sys.exit(0)
            try:
                logger.debug(
                    "Calling init_storagetype() for postgres: {} {}".format(
                        self.name_json, self.key_json
                    )
                )
                init_storagetype = stg_lib["init_storagetype"]
                c_config = c_char_p(self.name_json.encode("utf-8"))
                c_credentials = c_char_p(self.key_json.encode("utf-8"))
                result = init_storagetype(c_config, c_credentials)
                logger.debug(" ... returns {}".format(result))
            except RuntimeError as e:
                logger.error("Error initializing storage, ignoring ... {}".format(e))

    async def set_wallet(self):
        try:
            await wallet.create_wallet(self.name_json, self.key_json)
            return True
        except IndyError as ex:
            if ex.error_code == ErrorCode.WalletAlreadyExistsError:
                logger.info("Wallet " + self.name + " already exists")
                return True
            else:
                logger.error(ex)
                return False

    async def open_wallet(self):
        try:
            self.handle = await wallet.open_wallet(self.name_json, self.key_json)
            logger.info("Wallet handle {}".format(self.handle))
            return self.handle
        except IndyError as e:
            logger.error(e)
            return None

    def get_wallet_handle(self):
        return self.handle
