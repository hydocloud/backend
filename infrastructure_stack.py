from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_rds as rds,
    aws_ec2 as ec2,
)
import os
import subprocess


class InfrastructureStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Databases
        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        postgres_db = (
            rds.DatabaseInstance(
                self,
                "RDS",
                database_name="db1",
                engine=rds.DatabaseInstanceEngine.postgres(
                    version=rds.PostgresEngineVersion.VER_12_4
                ),
                vpc=vpc,
                port=5432,
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.BURSTABLE3,
                    ec2.InstanceSize.MICRO,
                ),
                removal_policy=core.RemovalPolicy.DESTROY,
                deletion_protection=False,
                credentials=rds.Credentials.from_username("loginService"),
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            ),
        )
        postgres_db.connections.allowFromAnyIpv4(ec2.Port.tcp(5432))

        session_table = dynamodb.Table(
            self,
            "session",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
        )
        nonce_table = dynamodb.Table(
            self,
            "nonces",
            partition_key=dynamodb.Attribute(
                name="service_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="message", type=dynamodb.AttributeType.STRING
            ),
        )

        # Lambda layer
        indy_sdk_postgres_layer = _lambda.LayerVersion(
            self,
            "indy-sdk-postgres",
            code=_lambda.Code.asset("../microservices/Login/indysdk-postgres.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
        )

        # The code that defines your stack goes here
        generate_session_lambda = _lambda.Function(
            self,
            "GenerateSession",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset("../microservices/Login/generate_session"),
            handler="app.lambda_handler",
            environment={
                "SESSION_TABLE_NAME": session_table.table_name,
                "LOGIN_ID": "0b4ea276-62f8-4e2c-8dd5-e8318b6366dc",
                "JWT_SECRET": "secret",
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
            layers=[
                self.create_dependencies_layer(
                    "test", "GenerateSession", "generate_session"
                )
            ],
        )
        generate_jwt_lambda = _lambda.Function(
            self,
            "GenerateJWT",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset("../microservices/Login/generate_jwt"),
            handler="app.lambda_handler",
            environment={
                "SESSION_TABLE_NAME": session_table.table_name,
                "JWT_SECRET": "secret",
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
            layers=[
                self.create_dependencies_layer("test", "GenerateJWT", "generate_jwt")
            ],
        )
        validate_nonce_lambda = _lambda.Function(
            self,
            "ValidateNonce",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/Login/validate_nonce"),
            handler="app.lambda_handler",
            environment={
                "LOGIN_ID": "0b4ea276-62f8-4e2c-8dd5-e8318b6366dc",
                "LOGIN_SERVICE_PASSWORD": "secret",
                "DB_PORT": "5432",
                "DB_HOST": "irtzilmhogi0v.cnlv3anezp7g.eu-west-1.rds.amazonaws.com",
                "DB_NAME": "wallets",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "QOrcnW^FI5DHdWMqDP=4hvgsmYQv,G",
                "NONCE_TABLE_NAME": nonce_table.table_name,
                "SESSION_TABLE_NAME": session_table.table_name,
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
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
            code=_lambda.Code.asset("../microservices/Login/login_service"),
            handler="app.lambda_handler",
            environment={
                "LOGIN_ID": "0b4ea276-62f8-4e2c-8dd5-e8318b6366dc",
                "ONBOARDING_PATH": "http://test.hydo.cloud:60050/onboarding",
                "LOGIN_SERVICE_PASSWORD": "secret",
                "WALLET_PATH": "/Users/riccardo/hydo/platform/microservices/Login/tmp",
                "DB_PORT": "5432",
                "DB_HOST": "irtzilmhogi0v.cnlv3anezp7g.eu-west-1.rds.amazonaws.com",
                "DB_NAME": "wallets",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "QOrcnW^FI5DHdWMqDP=4hvgsmYQv,G",
                "NONCE_TABLE_NAME": nonce_table.table_name,
                "DYNAMODB_ENDPOINT_OVERRIDE": "",
            },
            layers=[
                indy_sdk_postgres_layer,
                self.create_dependencies_layer("test", "LoginService", "login_service"),
            ],
        )

        # Lambda - DynamoDB permissions
        session_table.grant_write_data(generate_session_lambda)
        session_table.grant_read_write_data(generate_jwt_lambda)
        nonce_table.grant_read_data(validate_nonce_lambda)
        nonce_table.grant_write_data(login_service_lambda)

        #  Api gateway
        api = apigw.RestApi(self, "login-api", rest_api_name="Login Service")
        generate_session_integration = apigw.LambdaIntegration(generate_session_lambda)
        generate_session_resource = api.root.add_resource("session")
        generate_session_resource.add_method("GET", generate_session_integration)
        generate_jwt_integration = apigw.LambdaIntegration(generate_jwt_lambda)
        generate_jwt_resource = generate_session_resource.add_resource("{id}")
        generate_jwt_resource.add_method("GET", generate_jwt_integration)
        login_service_integration = apigw.LambdaIntegration(login_service_lambda)
        login_service_resource = api.root.add_resource("login")
        login_service_resource.add_method("POST", login_service_integration)
        validate_nonce_integration = apigw.LambdaIntegration(validate_nonce_lambda)
        validate_nonce_resource = login_service_resource.add_resource("validate")
        validate_nonce_resource.add_method("POST", validate_nonce_integration)

    def create_dependencies_layer(
        self, project_name, function_name, folder_name: str
    ) -> _lambda.LayerVersion:
        requirements_file = "../microservices/Login/{}/requirements.txt".format(
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