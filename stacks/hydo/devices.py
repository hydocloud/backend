from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigatewayv2_integrations as apigw2_integrations,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource


def lambdas(self):
    path = self.current_path

    create_device_group_lambda = _lambda.Function(
        self,
        "CreateDeviceGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset("{}/device/create_device_group".format(path)),
        handler="app.lambda_handler",
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "devices",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
        },
        layers=[
            self.create_dependencies_layer(
                "Depencendies", "CreateDeviceGroup", "/device/create_device_group"
            ),
            self.create_model_layer("ModelLayer", "CreateDeviceGroup", "/device"),
        ],
    )
    create_device_group_lambda.add_event_source(
        source=SqsEventSource(self.create_device_group_queue, batch_size=1)
    )

    # delete_device_groups_lambda = _lambda.Function(
    #     self,
    #     "DeleteDeviceGroup",
    #     runtime=_lambda.Runtime.PYTHON_3_8,
    #     code=_lambda.Code.asset("{}/device/delete_device_groups".format(path)),
    #     handler="app.lambda_handler",
    #     tracing=_lambda.Tracing.ACTIVE,
    #     environment={
    #         "DB_PORT": self.rds.db_instance_endpoint_port,
    #         "DB_HOST": self.rds.db_instance_endpoint_address,
    #         "DB_NAME": "devices",
    #         "DB_ENGINE": "postgresql",
    #         "DB_USER": "loginService",
    #         "DB_PASSWORD": "ciaociao",
    #     },
    #     layers=[
    #         self.create_dependencies_layer(
    #             "Depencendies", "DeleteDeviceGroup", "/device/delete_device_groups"
    #         ),
    #         self.create_model_layer("ModelLayer", "DeleteDeviceGroup", "/device"),
    #     ],
    # )

    # edit_device_groups_lambda = _lambda.Function(
    #     self,
    #     "EditDeviceGroup",
    #     runtime=_lambda.Runtime.PYTHON_3_8,
    #     code=_lambda.Code.asset("{}/device/edit_device_group".format(path)),
    #     handler="app.lambda_handler",
    #     tracing=_lambda.Tracing.ACTIVE,
    #     environment={
    #         "DB_PORT": self.rds.db_instance_endpoint_port,
    #         "DB_HOST": self.rds.db_instance_endpoint_address,
    #         "DB_NAME": "devices",
    #         "DB_ENGINE": "postgresql",
    #         "DB_USER": "loginService",
    #         "DB_PASSWORD": "ciaociao",
    #     },
    #     layers=[
    #         self.create_dependencies_layer(
    #             "Depencendies", "EditDeviceGroup", "/device/edit_device_group"
    #         ),
    #         self.create_model_layer("ModelLayer", "EditDeviceGroup", "/device"),
    #     ],
    # )

    # get_device_groups_lambda = _lambda.Function(
    #     self,
    #     "GetDeviceGroups",
    #     runtime=_lambda.Runtime.PYTHON_3_8,
    #     code=_lambda.Code.asset("{}/device/get_device_groups".format(path)),
    #     handler="app.lambda_handler",
    #     tracing=_lambda.Tracing.ACTIVE,
    #     environment={
    #         "DB_PORT": self.rds.db_instance_endpoint_port,
    #         "DB_HOST": self.rds.db_instance_endpoint_address,
    #         "DB_NAME": "devices",
    #         "DB_ENGINE": "postgresql",
    #         "DB_USER": "loginService",
    #         "DB_PASSWORD": "ciaociao",
    #     },
    #     layers=[
    #         self.create_dependencies_layer(
    #             "Depencendies", "GetDeviceGroup", "/device/get_device_groups"
    #         ),
    #         self.create_model_layer("ModelLayer", "GetDeviceGroup", "/device"),
    #     ],
    # )

    self.http_api.add_routes(
        path="/devices/groups",
        methods=[HttpMethod.POST],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=create_device_group_lambda
        ),
    )

    # self.http_api.add_routes(
    #     path="/devices/groups/{id}",
    #     methods=[HttpMethod.PUT],
    #     integration=apigw2_integrations.LambdaProxyIntegration(
    #         handler=edit_device_groups_lambda
    #     ),
    # )

    # self.http_api.add_routes(
    #     path="/devices/groups/{id}",
    #     methods=[HttpMethod.DELETE],
    #     integration=apigw2_integrations.LambdaProxyIntegration(
    #         handler=delete_device_groups_lambda
    #     ),
    # )

    # self.http_api.add_routes(
    #     path="/devices/groups",
    #     methods=[HttpMethod.GET],
    #     integration=apigw2_integrations.LambdaProxyIntegration(
    #         handler=get_device_groups_lambda
    #     ),
    # )

    # self.http_api.add_routes(
    #     path="/devices/groups/{id}",
    #     methods=[HttpMethod.GET],
    #     integration=apigw2_integrations.LambdaProxyIntegration(
    #         handler=get_device_groups_lambda
    #     ),
    # )
