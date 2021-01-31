from aws_cdk import (
    aws_lambda as _lambda,
    aws_lambda_python as lambda_python,
    aws_apigatewayv2_integrations as apigw2_integrations,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secret_manager,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_dynamodb import BillingMode
from aws_cdk.core import Duration
from utils.prefix import env_specific

LAMBDA_HANDLER = "app.lambda_handler"
LAMBDAS_FOLDER = "/authorization"


def lambdas(self, device_secret_key: secret_manager.Secret):
    PATH = self.current_path

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

    indy_sdk_postgres_layer = _lambda.LayerVersion(
        self,
        env_specific("indy-sdk-postgres"),
        code=_lambda.Code.asset(
            "{}/authorization/indysdk-postgres.zip".format(self.current_path)
        ),
        compatible_runtimes=[_lambda.Runtime.PYTHON_3_7, _lambda.Runtime.PYTHON_3_8],
    )

    create_authorization_lambda = lambda_python.PythonFunction(
        self,
        "CreateAuthorization",
        entry=f"{PATH}{LAMBDAS_FOLDER}/create_authorization",
        index="app.py",
        handler="lambda_handler",
        runtime=_lambda.Runtime.PYTHON_3_8,
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "authorizations",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_model_layer(
                "ModelLayer", "CreateAuthorization", LAMBDAS_FOLDER
            ),
        ],
    )

    create_authorization_lambda.add_event_source(
        source=SqsEventSource(self.create_authorization_device_queue, batch_size=1)
    )

    delete_authorization_lambda = lambda_python.PythonFunction(
        self,
        "DeleteAuthorization",
        runtime=_lambda.Runtime.PYTHON_3_8,
        entry=f"{PATH}{LAMBDAS_FOLDER}/delete_authorization",
        index="app.py",
        handler="lambda_handler",
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "authorizations",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_model_layer(
                "ModelLayer", "DeleteAuthorization", LAMBDAS_FOLDER
            ),
        ],
    )

    edit_authorization_lambda = lambda_python.PythonFunction(
        self,
        "EditAuthorization",
        runtime=_lambda.Runtime.PYTHON_3_8,
        entry=f"{PATH}{LAMBDAS_FOLDER}/edit_authorization",
        index="app.py",
        handler="lambda_handler",
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "authorizations",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_model_layer(
                "ModelLayer", "EditAuthorization", "/authorization"
            ),
        ],
    )

    get_authorizations_lambda = lambda_python.PythonFunction(
        self,
        "GetAuthorizations",
        runtime=_lambda.Runtime.PYTHON_3_8,
        entry=f"{PATH}{LAMBDAS_FOLDER}/get_authorizations",
        index="app.py",
        handler="lambda_handler",
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "authorizations",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_model_layer("ModelLayer", "GetAuthorization", LAMBDAS_FOLDER),
        ],
    )

    self.http_api.add_routes(
        path="/authorizations",
        methods=[HttpMethod.POST],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=create_authorization_lambda
        ),
    )

    self.http_api.add_routes(
        path="/authorizations/{id}",
        methods=[HttpMethod.PUT],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=edit_authorization_lambda
        ),
    )

    self.http_api.add_routes(
        path="/authorizations/{id}",
        methods=[HttpMethod.DELETE],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=delete_authorization_lambda
        ),
    )

    self.http_api.add_routes(
        path="/authorizations",
        methods=[HttpMethod.GET],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=get_authorizations_lambda
        ),
    )

    self.http_api.add_routes(
        path="/authorizations/{id}",
        methods=[HttpMethod.GET],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=get_authorizations_lambda
        ),
    )

    authorization_service_lambda = lambda_python.PythonFunction(
        self,
        "AuthorizationService",
        entry=f"{PATH}{LAMBDAS_FOLDER}/authorization_service",
        index="app.py",
        handler="lambda_handler",
        runtime=_lambda.Runtime.PYTHON_3_8,
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "NONCE_TABLE_NAME": nonce_table.table_name,
            "SERVICE_ID": "bf7d5894-e852-4022-bbc0-abdb26fbc6d5",
            "DYNAMODB_ENDPOINT_OVERRIDE": "",
        },
        layers=[
            self.create_model_layer(
                "ModelLayer", "AuthorizationService", LAMBDAS_FOLDER
            ),
        ],
    )

    lambda_python.PythonFunction(
        self,
        "Onboarding",
        entry=f"{PATH}{LAMBDAS_FOLDER}/onboarding",
        index="app.py",
        handler="lambda_handler",
        runtime=_lambda.Runtime.PYTHON_3_8,
        tracing=_lambda.Tracing.ACTIVE,
        timeout=Duration.minutes(10),
        memory_size=512,
        environment={
            "AUTHORIZATION_ID": "bf7d5894-e852-4022-bbc0-abdb26fbc6d5",
            "ONBOARDING_PATH": "http://test.hydo.cloud:60050/onboarding",
            "DB_INDY_SERVICE_PASSWORD": "secret",
            "DB_INDY_SERVICE_NAME": "authorization_service",
            "DB_INDY_PORT": self.rds.db_instance_endpoint_port,
            "DB_INDY_HOST": self.rds.db_instance_endpoint_address,
            "DB_INDY_NAME": "wallets",
            "DB_INDY_ENGINE": "postgresql",
            "DB_INDY_USER": "authorizationService",
            "DB_INDY_PASSWORD": "ciaociao",
        },
        layers=[
            indy_sdk_postgres_layer,
            self.create_model_layer("ModelLayer", "Onboarding", LAMBDAS_FOLDER),
        ],
    )

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

    self.http_api.add_routes(
        path="/authz",
        methods=[HttpMethod.POST],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=authorization_service_lambda
        ),
    )

    self.http_api.add_routes(
        path="/authz/validate",
        methods=[HttpMethod.POST],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=validate_authorization_lambda
        ),
    )

    device_secret_key.grant_read(grantee=validate_authorization_lambda)
    nonce_table.grant_write_data(grantee=authorization_service_lambda)
    nonce_table.grant_read_data(grantee=validate_authorization_lambda)
