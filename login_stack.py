from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_rds as rds,
    aws_route53 as route53,
    aws_certificatemanager as certificate_manager,
    aws_ec2 as ec2,
)
from aws_cdk.core import Duration
import os
import subprocess
from utils.prefix import env_specific, domain_specific


class LoginStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, rds: rds, route53: route53, certificate_manager: certificate_manager, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Databases
        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        session_table = dynamodb.Table(
            self,
            env_specific("sessions"),
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            time_to_live_attribute="expiration_time"
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
            time_to_live_attribute="expiration_time"
        )

        # Lambda layer
        indy_sdk_postgres_layer = _lambda.LayerVersion(
            self,
            env_specific("indy-sdk-postgres"),
            code=_lambda.Code.asset("../microservices/login/indysdk-postgres.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
        )

        # The code that defines your stack goes here
        generate_session_lambda = _lambda.Function(
            self,
            "GenerateSession",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/login/generate_session"),
            handler="app.lambda_handler",
            environment={
                "SESSION_TABLE_NAME": session_table.table_name,
                "LOGIN_ID": "0b4ea276-62f8-4e2c-8dd5-e8318b6366dc",
                "JWT_SECRET": "secret",
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
            tracing=_lambda.Tracing.ACTIVE,
            layers=[
                self.create_dependencies_layer(
                    "test", "GenerateSession", "generate_session"
                )
            ],
        )
        generate_jwt_lambda = _lambda.Function(
            self,
            "GenerateJWT",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/login/generate_jwt"),
            handler="app.lambda_handler",
            environment={
                "SESSION_TABLE_NAME": session_table.table_name,
                "JWT_SECRET": "secret",
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
            tracing=_lambda.Tracing.ACTIVE,
            layers=[
                self.create_dependencies_layer("test", "GenerateJWT", "generate_jwt")
            ],
        )
        validate_nonce_lambda = _lambda.Function(
            self,
            "ValidateNonce",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/login/validate_nonce"),
            handler="app.lambda_handler",
            timeout=Duration.seconds(350),
            memory_size=512,
            environment={
                "LOGIN_ID": "0b4ea276-62f8-4e2c-8dd5-e8318b6366dc",
                "LOGIN_SERVICE_PASSWORD": "secret",
                "DB_PORT": rds.db_instance_endpoint_port,
                "DB_HOST": rds.db_instance_endpoint_address,
                "DB_NAME": "wallets",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "ciaociao",
                "NONCE_TABLE_NAME": nonce_table.table_name,
                "SESSION_TABLE_NAME": session_table.table_name,
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
            tracing=_lambda.Tracing.ACTIVE,
            layers=[
                indy_sdk_postgres_layer,
                self.create_dependencies_layer(
                    "test", "ValidateNonce", "validate_nonce"
                ),
            ],
        )
        login_service_lambda = _lambda.Function(
            self,
            "LoginService",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/login/login_service"),
            handler="app.lambda_handler",
            timeout=Duration.seconds(350),
            memory_size=512,
            environment={
                "LOGIN_ID": "0b4ea276-62f8-4e2c-8dd5-e8318b6366dc",
                "ONBOARDING_PATH": "http://test.hydo.cloud:60050/onboarding",
                "LOGIN_SERVICE_PASSWORD": "secret",
                "WALLET_PATH": "/Users/riccardo/hydo/platform/microservices/login/tmp",
                "DB_PORT": rds.db_instance_endpoint_port,
                "DB_HOST": rds.db_instance_endpoint_address,
                "DB_NAME": "wallets",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "ciaociao",
                "NONCE_TABLE_NAME": nonce_table.table_name,
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
            tracing=_lambda.Tracing.ACTIVE,
            layers=[
                indy_sdk_postgres_layer,
                self.create_dependencies_layer("test", "LoginService", "login_service"),
            ],
        )
        onboarding_lambda = _lambda.Function(
            self,
            "Onboarding",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/login/onboarding"),
            handler="app.lambda_handler",
            timeout=Duration.seconds(350),
            memory_size=512,
            environment={
                "LOGIN_ID": "0b4ea276-62f8-4e2c-8dd5-e8318b6366dc",
                "ONBOARDING_PATH": "http://test.hydo.cloud:60050/onboarding",
                "LOGIN_SERVICE_PASSWORD": "secret",
                "WALLET_PATH": "/Users/riccardo/hydo/platform/microservices/login/tmp",
                "DB_PORT": "5432",
                "DB_HOST": "irtzilmhogi0v.cnlv3anezp7g.eu-west-1.rds.amazonaws.com",
                "DB_NAME": "wallets",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "ciaociao",
                "NONCE_TABLE_NAME": nonce_table.table_name,
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
            tracing=_lambda.Tracing.ACTIVE,
            layers=[
                indy_sdk_postgres_layer,
                self.create_dependencies_layer("test", "Onboarding", "onboarding"),
            ],
        )

        # Lambda - DynamoDB permissions
        session_table.grant_write_data(generate_session_lambda)
        session_table.grant_read_write_data(generate_jwt_lambda)
        session_table.grant_read_write_data(validate_nonce_lambda)
        nonce_table.grant_read_data(validate_nonce_lambda)
        nonce_table.grant_write_data(login_service_lambda)

        #  Api gateway
        
        self.api = apigw.RestApi(
            self, 
            "login-api", 
            rest_api_name=env_specific("login-service")
        )
        generate_session_integration = apigw.LambdaIntegration(generate_session_lambda)
        generate_session_resource = self.api.root.add_resource("session")
        generate_session_resource.add_method("GET", generate_session_integration)
        generate_jwt_integration = apigw.LambdaIntegration(generate_jwt_lambda)
        generate_jwt_resource = generate_session_resource.add_resource("{id}")
        generate_jwt_resource.add_method("GET", generate_jwt_integration)
        login_service_integration = apigw.LambdaIntegration(login_service_lambda)
        login_service_resource = self.api.root.add_resource("login")
        login_service_resource.add_method("POST", login_service_integration)
        validate_nonce_integration = apigw.LambdaIntegration(validate_nonce_lambda)
        validate_nonce_resource = login_service_resource.add_resource("validate")
        validate_nonce_resource.add_method("POST", validate_nonce_integration)
        
        # Add certificate and cname
        certificate = certificate_manager.issue_certificate(env_specific('login-api'), domain_specific('api', 'login'))
        self.api.add_domain_name(
            domain_specific('api', 'login'),
            domain_name='{}.{}'.format(domain_specific('api', 'login'), route53.get_domain_name()),
            certificate=certificate,
            endpoint_type=apigw.EndpointType.REGIONAL,
            security_policy=apigw.SecurityPolicy.TLS_1_2
        )
        route53.add_api_gateway_record('api.dev.login', self.api)

    def create_dependencies_layer(self, project_name, function_name, folder_name: str) -> _lambda.LayerVersion:
        requirements_file = "../microservices/login/{}/requirements.txt".format(
            folder_name
        )
        output_dir = ".lambda_dependencies/" + function_name

        # Install requirements for layer in the output_dir
        if not os.environ.get("SKIP_PIP"):
            # Note: Pip will create the output dir if it does not exist
            subprocess.check_call(
                f"pip install -r {requirements_file} -t {output_dir}/python".split()
            )
        return _lambda.LayerVersion(
            self,
            project_name + "-" + function_name + "-dependencies",
            code=_lambda.Code.from_asset(output_dir),
        )
         
    def api_gateway(self):
        return self.api
    def rds(self):
        return rds