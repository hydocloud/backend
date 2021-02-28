import pathlib
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secret_manager,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_dynamodb import BillingMode
from aws_cdk.core import Duration
from models._lambda import LambdaPython
from utils.prefix import env_specific

LAMBDA_HANDLER = "app.lambda_handler"
LAMBDAS_FOLDER = "/authorization"


def lambdas(self, device_secret_key: secret_manager.Secret):
    PATH = self.current_path

    indy_layer = self.__indy_layer()

    nonce_table = dynamodb.Table(
        self,
        env_specific("nonces-authorization"),
        partition_key=dynamodb.Attribute(
            name="service_id", type=dynamodb.AttributeType.STRING
        ),
        sort_key=dynamodb.Attribute(name="message", type=dynamodb.AttributeType.STRING),
        time_to_live_attribute="expiration_time",
        billing_mode=BillingMode.PAY_PER_REQUEST,
    )

    create_authorization_lambda = LambdaPython(
        self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/create_authorization",
        name="CreateAuthorization",
    )
    create_authorization_lambda.set_function()
    create_authorization_lambda.add_db_environment(
        db_host=self.rds.db_instance_endpoint_address,
        db_name="authorizations",
        db_user="loginService",
        db_password="ciaociao",
    )
    create_authorization_lambda.add_layer(models=True)

    create_authorization_lambda._lambda.add_event_source(
        source=SqsEventSource(self.create_authorization_device_queue, batch_size=1)
    )

    delete_authorization_lambda = LambdaPython(
        self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/delete_authorization",
        name="DeleteAuthorization",
    )
    delete_authorization_lambda.set_function()
    delete_authorization_lambda.add_db_environment(
        db_host=self.rds.db_instance_endpoint_address,
        db_name="authorizations",
        db_user="loginService",
        db_password="ciaociao",
    )
    delete_authorization_lambda.add_layer(models=True)

    edit_authorization_lambda = LambdaPython(
        self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/edit_authorization",
        name="EditAuthorization",
    )
    edit_authorization_lambda.set_function()
    edit_authorization_lambda.add_db_environment(
        db_host=self.rds.db_instance_endpoint_address,
        db_name="authorizations",
        db_user="loginService",
        db_password="ciaociao",
    )
    edit_authorization_lambda.add_layer(models=True)

    get_authorizations_lambda = LambdaPython(
        self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/edit_authorization",
        name="EditAuthorization",
    )
    get_authorizations_lambda.set_function()
    get_authorizations_lambda.add_db_environment(
        db_host=self.rds.db_instance_endpoint_address,
        db_name="authorizations",
        db_user="loginService",
        db_password="ciaociao",
    )
    get_authorizations_lambda.add_layer(models=True)

    self.apigateway.add_route(
        path="/authorizations",
        method=HttpMethod.POST,
        lambda_handler=create_authorization_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/authorizations/{id}",
        method=HttpMethod.PUT,
        lambda_handler=edit_authorization_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/authorizations/{id}",
        method=HttpMethod.DELETE,
        lambda_handler=delete_authorization_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/authorizations",
        method=HttpMethod.GET,
        lambda_handler=get_authorizations_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/authorizations/{id}",
        method=HttpMethod.GET,
        lambda_handler=get_authorizations_lambda._lambda,
    )

    authorization_service_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/authorization_service",
        name="AuthorizationService",
    )
    authorization_service_lambda.set_function()
    authorization_service_lambda.add_layer(models=True)
    authorization_service_lambda.add_environment(
        key="NONCE_TABLE_NAME", value=nonce_table.table_name
    )
    authorization_service_lambda.add_environment(
        key="SERVICE_ID", value="bf7d5894-e852-4022-bbc0-abdb26fbc6d5"
    )
    authorization_service_lambda.add_environment(
        key="DYNAMODB_ENDPOINT_OVERRIDE", value=""
    )

    onboarding_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/onboarding",
        name="Onboarding",
    )
    onboarding_lambda.set_function()
    onboarding_lambda.add_layer(models=True, layer_version=indy_layer)
    onboarding_lambda.add_environment(
        key="ONBOARDING_PATH", value="http://test.hydo.cloud:60050/onboarding"
    )
    onboarding_lambda.add_environment(
        key="AUTHORIZATION_ID", value="bf7d5894-e852-4022-bbc0-abdb26fbc6d5"
    )
    onboarding_lambda.add_environment(key="DB_INDY_SERVICE_PASSWORD", value="secret")
    onboarding_lambda.add_environment(
        key="DB_INDY_SERVICE_NAME", value="authorization_service"
    )
    onboarding_lambda.add_environment(
        key="DB_INDY_PORT", value=self.rds.db_instance_endpoint_port
    )
    onboarding_lambda.add_environment(
        key="DB_INDY_HOST", value=self.rds.db_instance_endpoint_address
    )
    onboarding_lambda.add_environment(key="DB_INDY_NAME", value="wallets")
    onboarding_lambda.add_environment(key="DB_INDY_ENGINE", value="postgresql")
    onboarding_lambda.add_environment(key="DB_INDY_USER", value="authorizationService")
    onboarding_lambda.add_environment(key="DB_INDY_PASSWORD", value="ciaociao")

    ecr_image = _lambda.EcrImageCode.from_asset_image(
        directory=f"{PATH}{LAMBDAS_FOLDER}", file="Docker_validate_authorization"
    )

    validate_authorization_lambda = _lambda.Function(
        self,
        "ValidateAuthorization",
        code=ecr_image,
        handler=_lambda.Handler.FROM_IMAGE,
        runtime=_lambda.Runtime.FROM_IMAGE,
        tracing=_lambda.Tracing.ACTIVE,
        timeout=Duration.minutes(10),
        memory_size=512,
        environment={
            "AUTHORIZATION_ID": "bf7d5894-e852-4022-bbc0-abdb26fbc6d5",
            "DB_INDY_SERVICE_PASSWORD": "secret",
            "DB_INDY_SERVICE_NAME": "authorization_service",
            "DB_INDY_PORT": self.rds.db_instance_endpoint_port,
            "DB_INDY_HOST": self.rds.db_instance_endpoint_address,
            "DB_INDY_NAME": "wallets",
            "DB_INDY_ENGINE": "postgresql",
            "DB_INDY_USER": "authorizationService",
            "DB_INDY_PASSWORD": "ciaociao",
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_ENGINE": "postgresql",
            "DB_NAME_DEVICES": "devices",
            "DB_USER_DEVICES": "loginService",
            "DB_PASSWORD_DEVICES": "ciaociao",
            "DB_NAME_AUTHORIZATIONS": "authorizations",
            "DB_USER_AUTHORIZATIONS": "loginService",
            "DB_PASSWORD_AUTHORIZATIONS": "ciaociao",
            "SECRET_NAME": device_secret_key.secret_arn,
            "NONCE_TABLE_NAME": nonce_table.table_name,
            "SERVICE_ID": "bf7d5894-e852-4022-bbc0-abdb26fbc6d5",
            "DYNAMODB_ENDPOINT_OVERRIDE": "",
        },
    )

    self.apigateway.add_route(
        path="/authz",
        method=HttpMethod.POST,
        lambda_handler=authorization_service_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/authz/validate",
        method=HttpMethod.POST,
        lambda_handler=validate_authorization_lambda,
    )

    device_secret_key.grant_read(grantee=validate_authorization_lambda)
    nonce_table.grant_write_data(grantee=authorization_service_lambda._lambda)
    nonce_table.grant_read_data(grantee=validate_authorization_lambda)


def __indy_layer(self):
    return _lambda.LayerVersion(
        self,
        env_specific("indy-sdk-postgres"),
        code=_lambda.Code.asset(
            f"{str(pathlib.Path().absolute())}/microservices/indysdk-postgres.zip"
        ),
        compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
    )
