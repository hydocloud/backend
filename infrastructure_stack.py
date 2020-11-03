from aws_cdk import core, aws_lambda as _lambda, aws_apigateway as apigw


class InfrastructureStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        indy_sdk_postgres_layer = _lambda.LayerVersion(
            self,
            "indy-sdk-postgres",
            code=_lambda.Code.asset("../microservices/Login/indysdk-postgres.zip"),
            compatible_runtimes= [_lambda.Runtime.PYTHON_3_8],
        )

        # The code that defines your stack goes here
        generate_session_kambda = _lambda.Function(
            self,
            "GenerateSession",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset("../microservices/Login/generate_session"),
            handler="app.handler",
        )
        generate_jwt_lambda = _lambda.Function(
            self,
            "GenerateJWT",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset("../microservices/Login/generate_jwt"),
            handler="app.handler",
        )
        validate_nonce_lambda = _lambda.Function(
            self,
            "ValidateNonce",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/Login/validate_nonce"),
            handler="app.handler",
            layers=[indy_sdk_postgres_layer]
        )
        login_service_lambda = _lambda.Function(
            self,
            "LoginService",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/Login/login_service"),
            handler="app.handler",
            layers=[indy_sdk_postgres_layer]
        )