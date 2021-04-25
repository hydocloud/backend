from aws_cdk import (
    aws_secretsmanager as secret_manager,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from models._lambda import LambdaPython

LAMBDA_HANDLER = "app.lambda_handler"
LAMBDAS_FOLDER = "/device/src"


def lambdas(self, device_secret_key: secret_manager.Secret):
    PATH = self.current_path
    db_name = "devices"
    db_user = "loginService"
    db_password = "ciaociao"
    db_host = self.rds.db_instance_endpoint_address

    create_device_group_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/create_device_group",
        name="CreateDeviceGroup",
    )
    create_device_group_lambda.set_function()
    create_device_group_lambda.add_layer(layer_version=self.model_layer)
    create_device_group_lambda.add_db_environment(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )

    create_device_group_lambda._lambda.add_event_source(
        source=SqsEventSource(self.create_device_group_queue, batch_size=1)
    )

    delete_device_group_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/delete_device_group",
        name="DeleteDeviceGroup",
    )
    delete_device_group_lambda.set_function()
    delete_device_group_lambda.add_layer(layer_version=self.model_layer)
    delete_device_group_lambda.add_db_environment(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )

    edit_device_group_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/edit_device_group",
        name="EditDeviceGroup",
    )
    edit_device_group_lambda.set_function()
    edit_device_group_lambda.add_layer(layer_version=self.model_layer)
    edit_device_group_lambda.add_db_environment(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )

    get_device_groups_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/get_device_groups",
        name="GetDeviceGroups",
    )
    get_device_groups_lambda.set_function()
    get_device_groups_lambda.add_layer(layer_version=self.model_layer)
    get_device_groups_lambda.add_db_environment(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )

    self.apigateway.add_route(
        path="/devices/groups",
        method=HttpMethod.POST,
        lambda_handler=create_device_group_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/devices/groups/{id}",
        method=HttpMethod.PUT,
        lambda_handler=edit_device_group_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/devices/groups/{id}",
        method=HttpMethod.DELETE,
        lambda_handler=delete_device_group_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/devices/groups",
        method=HttpMethod.GET,
        lambda_handler=get_device_groups_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/devices/groups/{id}",
        method=HttpMethod.GET,
        lambda_handler=get_device_groups_lambda._lambda,
    )

    create_device_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/create_device",
        name="CreateDevice",
    )
    create_device_lambda.set_function()
    create_device_lambda.add_layer(layer_version=self.model_layer)
    create_device_lambda.add_db_environment(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )
    create_device_lambda.add_environment(
        key="SECRET_NAME", value=device_secret_key.secret_arn
    )
    create_device_lambda.add_environment(
        key="QUEUE_URL", value=self.create_authorization_device_queue.queue_url
    )

    create_device_lambda._lambda.add_event_source(
        source=SqsEventSource(self.create_authorization_device_queue, batch_size=1)
    )

    self.create_authorization_device_queue.grant_send_messages(
        grantee=create_device_lambda._lambda
    )

    device_secret_key.grant_read(grantee=create_device_lambda._lambda)

    delete_device_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/delete_device",
        name="DeleteDevice",
    )
    delete_device_lambda.set_function()
    delete_device_lambda.add_layer(layer_version=self.model_layer)
    delete_device_lambda.add_db_environment(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )

    edit_device_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/edit_device",
        name="EditDevice",
    )
    edit_device_lambda.set_function()
    edit_device_lambda.add_layer(layer_version=self.model_layer)
    edit_device_lambda.add_db_environment(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )

    get_devices_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{LAMBDAS_FOLDER}/get_devices",
        name="GetDevices",
    )
    get_devices_lambda.set_function()
    get_devices_lambda.add_layer(layer_version=self.model_layer)
    get_devices_lambda.add_db_environment(
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )

    self.apigateway.add_route(
        path="/devices",
        method=HttpMethod.POST,
        lambda_handler=create_device_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/devices/{id}",
        method=HttpMethod.PUT,
        lambda_handler=edit_device_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/devices/{id}",
        method=HttpMethod.DELETE,
        lambda_handler=delete_device_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/devices",
        method=HttpMethod.GET,
        lambda_handler=get_devices_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/devices/{id}",
        method=HttpMethod.GET,
        lambda_handler=get_devices_lambda._lambda,
    )
