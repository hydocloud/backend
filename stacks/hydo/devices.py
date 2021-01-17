from aws_cdk import (
    aws_lambda as _lambda,
    aws_lambda_python as lambda_python,
    aws_apigatewayv2_integrations as apigw2_integrations,
    aws_secretsmanager as secret_manager
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource

LAMBDA_HANDLER = "app.lambda_handler"
DEVICE_FOLDER = "/device"


def lambdas(self, device_secret_key: secret_manager.Secret):
    PATH = self.current_path

    create_device_group_lambda = _lambda.Function(
        self,
        "CreateDeviceGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset(f"{PATH}{DEVICE_FOLDER}/create_device_group"),
        handler=LAMBDA_HANDLER,
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "devices",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao"
        },
        layers=[
            self.create_dependencies_layer(
                "Depencendies",
                "CreateDeviceGroup",
                f"{DEVICE_FOLDER}/create_device_group",
            ),
            self.create_model_layer("ModelLayer", "CreateDeviceGroup", DEVICE_FOLDER),
        ],
    )
    create_device_group_lambda.add_event_source(
        source=SqsEventSource(self.create_device_group_queue, batch_size=1)
    )

    delete_device_group_lambda = _lambda.Function(
        self,
        "DeleteDeviceGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset(f"{PATH}{DEVICE_FOLDER}/delete_device_group"),
        handler=LAMBDA_HANDLER,
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
                "Depencendies",
                "DeleteDeviceGroup",
                f"{DEVICE_FOLDER}/delete_device_group",
            ),
            self.create_model_layer("ModelLayer", "DeleteDeviceGroup", DEVICE_FOLDER),
        ],
    )

    edit_device_group_lambda = _lambda.Function(
        self,
        "EditDeviceGroup",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset(f"{PATH}/device/edit_device_group"),
        handler=LAMBDA_HANDLER,
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
                "Depencendies", "EditDeviceGroup", f"{DEVICE_FOLDER}/edit_device_group"
            ),
            self.create_model_layer("ModelLayer", "EditDeviceGroup", DEVICE_FOLDER),
        ],
    )

    get_device_groups_lambda = _lambda.Function(
        self,
        "GetDeviceGroups",
        runtime=_lambda.Runtime.PYTHON_3_8,
        code=_lambda.Code.asset(f"{PATH}{DEVICE_FOLDER}/get_device_groups"),
        handler=LAMBDA_HANDLER,
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
                "Depencendies", "GetDeviceGroup", f"{DEVICE_FOLDER}/get_device_groups"
            ),
            self.create_model_layer("ModelLayer", "GetDeviceGroup", DEVICE_FOLDER),
        ],
    )

    self.http_api.add_routes(
        path="/devices/groups",
        methods=[HttpMethod.POST],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=create_device_group_lambda
        ),
    )

    self.http_api.add_routes(
        path="/devices/groups/{id}",
        methods=[HttpMethod.PUT],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=edit_device_group_lambda
        ),
    )

    self.http_api.add_routes(
        path="/devices/groups/{id}",
        methods=[HttpMethod.DELETE],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=delete_device_group_lambda
        ),
    )

    self.http_api.add_routes(
        path="/devices/groups",
        methods=[HttpMethod.GET],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=get_device_groups_lambda
        ),
    )

    self.http_api.add_routes(
        path="/devices/groups/{id}",
        methods=[HttpMethod.GET],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=get_device_groups_lambda
        ),
    )

    create_device_lambda = lambda_python.PythonFunction(
        self,
        "CreateDevice",
        entry=f"{PATH}{DEVICE_FOLDER}/create_device",
        index="app.py",
        handler="lambda_handler",
        runtime=_lambda.Runtime.PYTHON_3_8,
        tracing=_lambda.Tracing.ACTIVE,
        environment={
            "DB_PORT": self.rds.db_instance_endpoint_port,
            "DB_HOST": self.rds.db_instance_endpoint_address,
            "DB_NAME": "devices",
            "DB_ENGINE": "postgresql",
            "DB_USER": "loginService",
            "DB_PASSWORD": "ciaociao",
            "SECRET_NAME": device_secret_key.secret_name,
        },
        layers=[
            self.create_model_layer("ModelLayer", "CreateDevice", DEVICE_FOLDER),
        ],
    )

    create_device_lambda.add_event_source(
        source=SqsEventSource(self.create_authorization_device_queue, batch_size=1)
    )

    device_secret_key.grant_read(grantee=create_device_lambda)

    delete_device_lambda = lambda_python.PythonFunction(
        self,
        "DeleteDevice",
        runtime=_lambda.Runtime.PYTHON_3_8,
        entry=f"{PATH}{DEVICE_FOLDER}/delete_device",
        index="app.py",
        handler="lambda_handler",
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
            self.create_model_layer("ModelLayer", "DeleteDevice", DEVICE_FOLDER),
        ],
    )

    edit_device_lambda = lambda_python.PythonFunction(
        self,
        "EditDevice",
        runtime=_lambda.Runtime.PYTHON_3_8,
        entry=f"{PATH}{DEVICE_FOLDER}/edit_device",
        index="app.py",
        handler="lambda_handler",
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
            self.create_model_layer("ModelLayer", "EditDevice", "/device"),
        ],
    )

    get_devices_lambda = lambda_python.PythonFunction(
        self,
        "GetDevices",
        runtime=_lambda.Runtime.PYTHON_3_8,
        entry=f"{PATH}{DEVICE_FOLDER}/get_devices",
        index="app.py",
        handler="lambda_handler",
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
            self.create_model_layer("ModelLayer", "GetDevice", DEVICE_FOLDER),
        ],
    )

    self.http_api.add_routes(
        path="/devices",
        methods=[HttpMethod.POST],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=create_device_lambda
        ),
    )

    self.http_api.add_routes(
        path="/devices/{id}",
        methods=[HttpMethod.PUT],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=edit_device_lambda
        ),
    )

    self.http_api.add_routes(
        path="/devices/{id}",
        methods=[HttpMethod.DELETE],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=delete_device_lambda
        ),
    )

    self.http_api.add_routes(
        path="/devices",
        methods=[HttpMethod.GET],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=get_devices_lambda
        ),
    )

    self.http_api.add_routes(
        path="/devices/{id}",
        methods=[HttpMethod.GET],
        integration=apigw2_integrations.LambdaProxyIntegration(
            handler=get_devices_lambda
        ),
    )
