""" Stack to deploy https certificate """

from aws_cdk import aws_secretsmanager as secret_manager


def device_symmetric_key(self) -> secret_manager.Secret:
    return secret_manager.Secret(
        self,
        "DeviceSecret",
        secret_name="DeviceSecret",
        generate_secret_string=secret_manager.SecretStringGenerator(password_length=32),
    )
