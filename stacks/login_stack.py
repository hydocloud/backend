""" Stack to deploy login service """
import pathlib
from aws_cdk import (
    core,
    aws_lambda,
    aws_dynamodb as dynamodb,
    aws_rds as rds,
    aws_route53 as route53,
    aws_certificatemanager as certificate_manager,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_dynamodb import BillingMode
from models.apigateway import Apigateway
from models._lambda import LambdaPython

from utils.prefix import env_specific, domain_specific


class LoginStack(core.Stack):
    """
    Class that deploy all services for login:
    LambdaPythons,
    Http api,
    Certificate
    Database
    """

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        rds_stack: rds,
        dns_stack: route53,
        certificate_stack: certificate_manager,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.current_path = str(pathlib.Path().absolute()) + "/microservices/login"

        indy_layer = self.__indy_layer()

        session_table = dynamodb.Table(
            self,
            env_specific("sessions"),
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            time_to_live_attribute="expiration_time",
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )
        nonce_table = dynamodb.Table(
            self,
            env_specific("nonces"),
            partition_key=dynamodb.Attribute(
                name="service_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="message", type=dynamodb.AttributeType.STRING
            ),
            time_to_live_attribute="expiration_time",
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        # The code that defines your stack goes here
        generate_session_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/generate_session",
            name="GenerateSession",
        )
        generate_session_lambda.set_function()
        generate_session_lambda.add_environment(
            key="SESSION_TABLE_NAME", value=session_table.table_name
        )
        generate_session_lambda.add_environment(
            key="LOGIN_ID", value="0b4ea276-62f8-4e2c-8dd5-e8318b6366dc"
        )
        generate_session_lambda.add_environment(key="JWT_SECRET", value="secret")
        generate_session_lambda.add_environment(
            key="DYNAMODB_ENDPOINT_OVERRIDE", value=""
        )

        generate_jwt_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/generate_jwt",
            name="GenerateJWT",
        )
        generate_jwt_lambda.set_function()
        generate_jwt_lambda.add_environment(
            key="SESSION_TABLE_NAME", value=session_table.table_name
        )
        generate_jwt_lambda.add_environment(key="JWT_SECRET", value="secret")
        generate_jwt_lambda.add_environment(key="DYNAMODB_ENDPOINT_OVERRIDE", value="")

        validate_nonce_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/validate_nonce",
            name="ValidateNonce",
        )
        validate_nonce_lambda.set_function()
        validate_nonce_lambda.add_layer(layer_version=indy_layer)
        validate_nonce_lambda.add_environment(
            key="SESSION_TABLE_NAME", value=session_table.table_name
        )
        validate_nonce_lambda.add_environment(key="JWT_SECRET", value="secret")
        validate_nonce_lambda.add_environment(
            key="DYNAMODB_ENDPOINT_OVERRIDE", value=""
        )
        validate_nonce_lambda.add_environment(
            key="LOGIN_ID", value="0b4ea276-62f8-4e2c-8dd5-e8318b6366dc"
        )
        validate_nonce_lambda.add_environment(
            key="LOGIN_SERVICE_PASSWORD", value="secret"
        )
        validate_nonce_lambda.add_environment(
            key="NONCE_TABLE_NAME", value=nonce_table.table_name
        )
        validate_nonce_lambda.add_db_environment(
            db_host=rds_stack.db_instance_endpoint_address,
            db_name="wallets",
            db_user="loginService",
            db_password="ciaociao",
        )

        login_service_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/login_service",
            name="LoginService",
        )
        login_service_lambda.set_function()
        login_service_lambda.add_layer(layer_version=indy_layer)
        login_service_lambda.add_environment(
            key="LOGIN_ID", value="0b4ea276-62f8-4e2c-8dd5-e8318b6366dc"
        )
        login_service_lambda.add_environment(
            key="ONBOARDING_PATH", value="http://test.hydo.cloud:60050/onboarding"
        )
        login_service_lambda.add_environment(
            key="LOGIN_SERVICE_PASSWORD", value="secret"
        )
        login_service_lambda.add_environment(
            key="NONCE_TABLE_NAME", value=nonce_table.table_name
        )
        login_service_lambda.add_environment(key="DYNAMODB_ENDPOINT_OVERRIDE", value="")
        login_service_lambda.add_db_environment(
            db_host=rds_stack.db_instance_endpoint_address,
            db_name="wallets",
            db_user="loginService",
            db_password="ciaociao",
        )

        onboarding_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/onboarding",
            name="Onboarding",
        )
        onboarding_lambda.set_function()
        onboarding_lambda.add_layer(layer_version=indy_layer)
        onboarding_lambda.add_environment(
            key="LOGIN_ID", value="0b4ea276-62f8-4e2c-8dd5-e8318b6366dc"
        )
        onboarding_lambda.add_environment(
            key="ONBOARDING_PATH", value="http://test.hydo.cloud:60050/onboarding"
        )
        onboarding_lambda.add_environment(key="LOGIN_SERVICE_PASSWORD", value="secret")
        onboarding_lambda.add_environment(
            key="NONCE_TABLE_NAME", value=nonce_table.table_name
        )
        onboarding_lambda.add_environment(key="DYNAMODB_ENDPOINT_OVERRIDE", value="")
        onboarding_lambda.add_db_environment(
            db_host=rds_stack.db_instance_endpoint_address,
            db_name="wallets",
            db_user="loginService",
            db_password="ciaociao",
        )

        # LambdaPython - DynamoDB permissions
        session_table.grant_write_data(generate_session_lambda._lambda)
        session_table.grant_read_write_data(generate_jwt_lambda._lambda)
        session_table.grant_read_write_data(validate_nonce_lambda._lambda)
        nonce_table.grant_read_data(validate_nonce_lambda._lambda)
        nonce_table.grant_write_data(login_service_lambda._lambda)

        #  Api gateway

        certificate = certificate_stack.issue_certificate(
            env_specific("login-api"), domain_specific("api", "login")
        )

        apigateway = Apigateway(
            current_stack=self, object_name="login-api-2", api_name="api-login"
        )

        apigateway.set_domain_name(
            prefix="api",
            logical_name="login",
            domain_name=dns_stack.get_domain_name(),
            certificate=certificate,
            mapping=True,
        )

        apigateway.add_route(
            path="/session",
            method=HttpMethod.GET,
            lambda_handler=generate_session_lambda._lambda,
        )
        apigateway.add_route(
            path="/session/{id}",
            method=HttpMethod.GET,
            lambda_handler=generate_jwt_lambda._lambda,
        )

        apigateway.add_route(
            path="/login",
            method=HttpMethod.POST,
            lambda_handler=login_service_lambda._lambda,
        )

        apigateway.add_route(
            path="/login/validate",
            method=HttpMethod.POST,
            lambda_handler=validate_nonce_lambda._lambda,
        )

        dns_stack.add_api_gateway_v2_record(
            "api.dev.login", apigateway.get_domain_name()
        )

    def __indy_layer(self):
        return aws_lambda.LayerVersion(
            self,
            env_specific("indy-sdk-postgres"),
            code=aws_lambda.Code.asset(
                f"{str(pathlib.Path().absolute())}/microservices/indysdk-postgres.zip"
            ),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8],
        )
