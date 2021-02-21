from aws_cdk import (
    aws_lambda as _lambda,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource

LAMBDA_HANDLER = "app.lambda_handler"


def lambdas(self):
    path = self.current_path

    create_user_groups_lambda = _lambda.Function(
        self,
        "CreateUserGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset("{}/user/create_user_groups".format(path)),
        handler=LAMBDA_HANDLER,
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
        source=SqsEventSource(self.create_user_group_queue, batch_size=1)
    )

    delete_user_groups_lambda = _lambda.Function(
        self,
        "DeleteUserGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset("{}/user/delete_user_groups".format(path)),
        handler=LAMBDA_HANDLER,
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
        handler=LAMBDA_HANDLER,
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
        handler=LAMBDA_HANDLER,
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

    self.apigateway.add_route(
        path="/users/groups",
        method=HttpMethod.POST,
        lambda_handler=create_user_groups_lambda,
    )

    self.apigateway.add_route(
        path="/users/groups/{id}",
        method=HttpMethod.PUT,
        lambda_handler=edit_user_groups_lambda,
    )

    self.apigateway.add_route(
        path="/users/groups/{id}",
        method=HttpMethod.DELETE,
        lambda_handler=delete_user_groups_lambda,
    )

    self.apigateway.add_route(
        path="/users/groups",
        method=HttpMethod.GET,
        lambda_handler=get_user_groups_lambda,
    )

    self.apigateway.add_route(
        path="/users/groups/{id}",
        method=HttpMethod.GET,
        lambda_handler=get_user_groups_lambda,
    )
