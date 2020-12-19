from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigatewayv2_integrations as apigw2_integrations,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource


def lambdas(self):
    path = self.current_path

    create_user_groups_lambda = _lambda.Function(
        self,
        "CreateUserGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset("{}/user/create_user_groups".format(path)),
        handler="app.lambda_handler",
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "users",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_dependencies_layer(
                "Depencendies", "CreateUserGroup", "/user/create_user_groups"
            ),
            self.create_model_layer("ModelLayer", "CreateUserGroup", "/user"),
        ],
    )
    create_user_groups_lambda.add_event_source(
        source=SqsEventSource(
            self.create_user_group_queue,
            batch_size=1
        )
    )

    delete_user_groups_lambda = _lambda.Function(
        self,
        "DeleteUserGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset("{}/user/delete_user_groups".format(path)),
        handler="app.lambda_handler",
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "users",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_dependencies_layer(
                "Depencendies", "DeleteUserGroup", "/user/delete_user_groups"
            ),
            self.create_model_layer("ModelLayer", "DeleteUserGroup", "/user"),
        ],
    )

    edit_user_groups_lambda = _lambda.Function(
        self,
        "EditUserGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset("{}/user/edit_user_group".format(path)),
        handler="app.lambda_handler",
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "users",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_dependencies_layer(
                "Depencendies", "EditUserGroup", "/user/edit_user_group"
            ),
            self.create_model_layer("ModelLayer", "EditUserGroup", "/user"),
        ],
    )

    get_user_groups_lambda = _lambda.Function(
        self,
        "GetUserGroups",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset("{}/user/get_user_groups".format(path)),
        handler="app.lambda_handler",
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "users",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_dependencies_layer(
                "Depencendies", "GetUserGroup", "/user/get_user_groups"
            ),
            self.create_model_layer("ModelLayer", "GetUserGroup", "/user"),
        ],
    )

    self.http_api.add_routes(
        path="/users/groups",
        methods=[HttpMethod.POST],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=create_user_groups_lambda
        ),
    )

    self.http_api.add_routes(
        path="/users/groups/{id}",
        methods=[HttpMethod.PUT],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=edit_user_groups_lambda
        ),
    )

    self.http_api.add_routes(
        path="/users/groups/{id}",
        methods=[HttpMethod.DELETE],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=delete_user_groups_lambda
        ),
    )

    self.http_api.add_routes(
        path="/users/groups",
        methods=[HttpMethod.GET],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=get_user_groups_lambda
        ),
    )

    self.http_api.add_routes(
        path="/users/groups/{id}",
        methods=[HttpMethod.GET],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=get_user_groups_lambda
        ),
    )
