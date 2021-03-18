import boto3
import logging
from os import environ
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from botocore.exceptions import ClientError
from aws_lambda_powertools import Tracer


tracer = Tracer(service="create_device")
logger = logging.getLogger(__name__)


def get_key(secret_manager=None) -> bytes:
    secret_name = environ["SECRET_NAME"]
    if secret_manager is None:
        session = boto3.session.Session()
        secret_manager = session.client(service_name="secretsmanager")

    try:
        get_secret_value_response = secret_manager.get_secret_value(
            SecretId=secret_name
        )
        logger.debug(f'key: {get_secret_value_response["SecretString"]}')
        return get_secret_value_response["SecretString"].encode()
    except ClientError as err:
        logger.error(err)
        raise err


def encrypt(data: str) -> bytes:
    key = get_key()
    iv = get_random_bytes(16)
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    logger.debug(f"hmac_key: {data}")
    return iv + cipher.encrypt(pad(data.encode("utf-8"), AES.block_size))
