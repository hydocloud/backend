"""Lambda that evaluate token and return authz policy"""
import logging
import os
import jwt


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)


def validate_token(token):
    """Decrypt token and return user_uuid"""
    secret = os.environ["JWT_SECRET"]
    try:
        res = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logger.error("Failed decode jwt")
        return False
    except jwt.InvalidSignatureError:
        logger.error("Failed decode jwt")
        return False
    return res


def lambda_handler(event, context):
    """Main function"""

    response = {"isAuthorized": False, "context": {}}

    user_token = event["headers"]["token"]
    res = validate_token(user_token)
    if res:
        response = {"isAuthorized": True, "context": {"sub": res["sub"]}}

    return response
