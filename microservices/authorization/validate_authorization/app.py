import logging
import asyncio
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
CONNECTION = None


async def init_wallet():
    global wallet_handle
    logger.info("Open wallet")
    if wallet_handle is None:
        x = Wallet.get_instance()
        wallet_handle = await x.open_wallet()


def lambda_handler(event, context) -> dict:

    global CONNECTION

    loop.run_until_complete(init_wallet())
    try:
        user_id = event["requestContext"]["authorizer"]["lambda"]["sub"]
        authz = AuthorizationClass(event["body"])
        device = DeviceClass(authz.unlock.deviceId)
    except Exception as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=400, body=Message(message="Bad request").json()
        ).dict()

    if CONNECTION is None:
        CONNECTION = init_db()
    try:
        authz.get_message()
    except Exception as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=404, body=Message(message="Not found").json()
        ).dict()

    try:
        loop.run_until_complete(authz.decrypt())
        key = device.get_secret_key()
        digest = authz.validation(
            user_id=user_id, connection=CONNECTION, device=device, key=key
        )
        if digest is None:
            return LambdaResponse(
                statusCode=404, body=Message(message="Not found").json()
            ).dict()
    except Exception as err:
        logger.error(err)
        return LambdaResponse(
            statusCode=500, body=Message(message="Internal server error").json()
        ).dict()

    return LambdaResponse(
        statusCode=200, body=UnlockModel(digest=digest, success=True).json()
    ).dict()
