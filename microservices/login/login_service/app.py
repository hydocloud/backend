import json
import logging
from models.wallet import Wallet
from store_nonce import store as store_nonce
import asyncio
import urllib3

loop = asyncio.get_event_loop()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
wallet_handle = None
did = None
verkey = None
http = urllib3.PoolManager()


async def init_wallet():
    global wallet_handle

    if wallet_handle is None:
        x = Wallet()
        wallet_handle = await x.open_wallet()


def lambda_handler(event, context):
    logger.info("Open wallet")
    loop.run_until_complete(init_wallet())
    try:
        payload = event["body"]
        encrypted_message = json.loads(payload)["message"]
    except KeyError as e:
        logger.error(e)

    res = store_nonce(encrypted_message)

    if res:
        return {"statusCode": 200, "body": json.dumps({"success": True})}

    return {"statusCode": 500, "body": json.dumps({"success": False})}
