import logging
import asyncio
import json
from models.api_response import LambdaResponse, UnlockModel, Message  # type: ignore
from models.wallet import Wallet  # type: ignore
from authorization import AuthorizationClass
from device import DeviceClass
from database import init_db


loop = asyncio.get_event_loop()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

wallet_handle = None
AUTHORIZATIONS_CONNECTION = None
DEVICES_CONNECTION = None


async def init_wallet():
    global wallet_handle
    logger.info("Open wallet")
    if wallet_handle is None:
        x = Wallet.get_instance()
        wallet_handle = await x.open_wallet()


def lambda_handler(event, context) -> dict:

    global AUTHORIZATIONS_CONNECTION, DEVICES_CONNECTION

    loop.run_until_complete(init_wallet())

    if AUTHORIZATIONS_CONNECTION is None or DEVICES_CONNECTION is None:
        AUTHORIZATIONS_CONNECTION, DEVICES_CONNECTION = init_db()

    try:
        logger.info(event)
        authz = AuthorizationClass(
            obj=json.loads(event["body"]), connection=AUTHORIZATIONS_CONNECTION
        )
        device = DeviceClass(
            device_id=authz.unlock.deviceId, connection=DEVICES_CONNECTION
        )
    except Exception as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()

    try:
        authz.get_message()
    except Exception as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=404, body=Message(message="Not found").json()
        ).dict()

    try:
        res, user_id = loop.run_until_complete(authz.decrypt())
        if res:
            key = device.get_secret_key()
            digest = authz.validation(user_id=user_id, device=device, key=key)
            if digest is None:
                return LambdaResponse(
                    statusCode=404, body=Message(message="Not found").json()
                ).dict()
        else:
            return LambdaResponse(
                statusCode=400, body=Message(message="Bad request").json()
            ).dict()
    except Exception as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()

    return LambdaResponse(
        statusCode=200, body=UnlockModel(digest=digest, success=True).json()
    ).dict()
