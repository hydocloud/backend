import json
import logging
from os import environ
from models.wallet import Wallet  # type: ignore
from models.did import DidVerkey  # type: ignore
import asyncio
import urllib3  # type: ignore

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
        await x.set_wallet()
        wallet_handle = await x.open_wallet()


async def init_did():
    global did, verkey
    onboardig_data = DidVerkey(wallet_handle)

    if did is None or verkey is None:
        await onboardig_data.create("onboarding")

    did, verkey = await onboardig_data.get_did_verkey("onboarding")
    logger.info("Did: {}, Verkey {}".format(did, verkey))


def onboarding():
    global did, verkey
    try:
        response = http.request(
            "POST",
            environ["ONBOARDING_PATH"],
            body=json.dumps(
                {"DidFrom": did, "Verkey": verkey, "Uuid": environ["LOGIN_ID"]}
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            retries=False,
        )
        logger.info(json.loads(response.data.decode("utf-8")))
    except urllib3.exceptions.NewConnectionError as e:
        logger.error(e)


def lambda_handler(event, context):
    logger.info("Create wallet object")
    loop.run_until_complete(init_wallet())
    loop.run_until_complete(init_did())
    onboarding()
