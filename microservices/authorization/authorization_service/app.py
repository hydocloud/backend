import json
import logging
from store_nonce import store as store_nonce  # type: ignore
import asyncio

loop = asyncio.get_event_loop()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


def lambda_handler(event, context):
    try:
        payload = event["body"]
        encrypted_message = json.loads(payload)["message"]
    except KeyError as e:
        logger.error(e)

    res = store_nonce(encrypted_message)

    if res:
        return {"statusCode": 200, "body": json.dumps({"success": True})}

    return {"statusCode": 500, "body": json.dumps({"success": False})}
