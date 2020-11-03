from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
)
import os
import subprocess


class InfrastructureStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        session_table = dynamodb.Table(
            self,
            "session",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
        )

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
                "DYNAMODB_ENDPOINT_OVERRIDE": ""
            },
            layers=[self.create_dependencies_layer("test", "GenerateSession")]
        )

        session_table.grant_write_data(generate_session_lambda)

        generate_jwt_lambda = _lambda.Function(
            self,
            "GenerateJWT",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset("../microservices/Login/generate_jwt"),
            handler="app.lambda_handler",
        )
        validate_nonce_lambda = _lambda.Function(
            self,
            "ValidateNonce",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/Login/validate_nonce"),
            handler="app.lambda_handler",
            layers=[indy_sdk_postgres_layer],
        )
        login_service_lambda = _lambda.Function(
            self,
            "LoginService",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/Login/login_service"),
            handler="app.lambda_handler",
            layers=[indy_sdk_postgres_layer],
        )

        apigw.LambdaRestApi(
            self,
            "Endpoint",
            handler=generate_session_lambda,
        )

    def create_dependencies_layer(
        self, project_name, function_name: str
    ) -> _lambda.LayerVersion:
        requirements_file = "../microservices/Login/generate_session/requirements.txt"
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