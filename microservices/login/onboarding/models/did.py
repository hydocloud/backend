import json
import logging
from indy import did
from indy.error import IndyError


logger = logging.getLogger(__name__)


class DidVerkey(object):
    def __init__(self, wallet_handle):
        self.wallet_handle = wallet_handle

    async def create(self, type):
        logger.info("Create Did and verkey")
        res = await self.get_did_verkey(type)
        if res is None:
            try:
                current_did, current_verkey = await did.create_and_store_my_did(
                    self.wallet_handle, "{}"
                )
                await did.set_did_metadata(self.wallet_handle, current_did, type)
                return current_did, current_verkey
            except IndyError as e:
                logger.error(e)
        return res

    async def get_did(self, type):
        did_list = await did.list_my_dids_with_meta(self.wallet_handle)
        did_list = json.loads(did_list)
        logger.info("Get Did")
        for mydid in did_list:
            if mydid["metadata"] == type:
                return mydid["did"]
        return None

    async def get_verkey(self, type):
        did_list = await did.list_my_dids_with_meta(self.wallet_handle)
        did_list = json.loads(did_list)
        logger.info("Get Verkey")
        for mydid in did_list:
            if mydid["metadata"] == type:
                return mydid["verkey"]

        return None

    async def get_did_verkey(self, type):
        did_list = await did.list_my_dids_with_meta(self.wallet_handle)
        did_list = json.loads(did_list)
        logger.info("Get Did and verkey")
        for mydid in did_list:
            if mydid["metadata"] == type:
                return mydid["did"], mydid["verkey"]
        return None
