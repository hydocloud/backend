from aws_cdk import (
    aws_secretsmanager as secret_manager,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from models._lambda import LambdaPython

LAMBDA_HANDLER = "app.lambda_handler"
DEVICE_FOLDER = "/device"


def lambdas(self, device_secret_key: secret_manager.Secret):
    PATH = self.current_path
    device_db_name = "devices"
    device_groups_db_name = "device_groups"
    db_user = "loginService"
    db_password = "ciaociao"
    db_host = self.rds.db_instance_endpoint_address

    create_device_group_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{DEVICE_FOLDER}/create_device_group",
        name="CreateDeviceGroup",
    )
    create_device_group_lambda.set_function()
    create_device_group_lambda.add_layer(models=True)
    create_device_group_lambda.add_db_environment(
        db_host=db_host,
        db_name=device_groups_db_name,
        db_user=db_user,
        db_password=db_password,
    )

    create_device_group_lambda._lambda.add_event_source(
        source=SqsEventSource(self.create_device_group_queue, batch_size=1)
    )

    delete_device_group_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{DEVICE_FOLDER}/delete_device_group",
        name="DeleteDeviceGroup",
    )
    delete_device_group_lambda.set_function()
    delete_device_group_lambda.add_layer(models=True)
    delete_device_group_lambda.add_db_environment(
        db_host=db_host,
        db_name=device_groups_db_name,
        db_user=db_user,
        db_password=db_password,
    )

    edit_device_group_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{DEVICE_FOLDER}/edit_device_group",
        name="EditDeviceGroup",
    )
    edit_device_group_lambda.set_function()
    edit_device_group_lambda.add_layer(models=True)
    edit_device_group_lambda.add_db_environment(
        db_host=db_host,
        db_name=device_groups_db_name,
        db_user=db_user,
        db_password=db_password,
    )

    get_device_groups_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{DEVICE_FOLDER}/get_device_groups",
        name="GetDeviceGroups",
    )
    get_device_groups_lambda.set_function()
    get_device_groups_lambda.add_layer(models=True)
    get_device_groups_lambda.add_db_environment(
        db_host=db_host,
        db_name=device_groups_db_name,
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
        code_path=f"{PATH}{DEVICE_FOLDER}/create_device",
        name="CreateDevice",
    )
    create_device_lambda.set_function()
    create_device_lambda.add_layer(models=True)
    create_device_lambda.add_db_environment(
        db_host=db_host,
        db_name=device_db_name,
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
        code_path=f"{PATH}{DEVICE_FOLDER}/delete_device",
        name="DeleteDevice",
    )
    delete_device_lambda.set_function()
    delete_device_lambda.add_layer(models=True)
    delete_device_lambda.add_db_environment(
        db_host=db_host,
        db_name=device_db_name,
        db_user=db_user,
        db_password=db_password,
    )

    edit_device_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{DEVICE_FOLDER}/edit_device",
        name="EditDevice",
    )
    edit_device_lambda.set_function()
    edit_device_lambda.add_layer(models=True)
    edit_device_lambda.add_db_environment(
        db_host=db_host,
        db_name=device_db_name,
        db_user=db_user,
        db_password=db_password,
    )

    get_devices_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{PATH}{DEVICE_FOLDER}/get_devices",
        name="GetDevices",
    )
    get_devices_lambda.set_function()
    get_devices_lambda.add_layer(models=True)
    get_devices_lambda.add_db_environment(
        db_host=db_host,
        db_name=device_db_name,
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
