from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from models._lambda import LambdaPython

LAMBDA_HANDLER = "app.lambda_handler"


def lambdas(self):
    path = self.current_path
    db_name = "users"
    db_user = "loginService"
    db_password = "ciaociao"
    db_host = self.rds.db_instance_endpoint_address

    create_user_groups_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{path}/user/create_user_groups",
        name="CreateUserGroup",
    )
    create_user_groups_lambda.set_function()
    create_user_groups_lambda.add_layer(models=True)
    create_user_groups_lambda.add_db_environment(
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        db_host=db_host
    )

    create_user_groups_lambda._lambda.add_event_source(
        source=SqsEventSource(self.create_user_group_queue, batch_size=1)
    )

    delete_user_groups_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{path}/user/delete_user_groups",
        name="DeleteUserGroup",
    )
    delete_user_groups_lambda.set_function()
    delete_user_groups_lambda.add_layer(models=True)
    delete_user_groups_lambda.add_db_environment(
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        db_host=db_host
    )

    edit_user_groups_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{path}/user/edit_user_group",
        name="EditUserGroup",
    )
    edit_user_groups_lambda.set_function()
    edit_user_groups_lambda.add_layer(models=True)
    edit_user_groups_lambda.add_db_environment(
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        db_host=db_host
    )

    get_user_groups_lambda = LambdaPython(
        current_stack=self,
        code_path=f"{path}/user/get_user_groups",
        name="GetUserGroups",
    )
    get_user_groups_lambda.set_function()
    get_user_groups_lambda.add_layer(models=True)
    get_user_groups_lambda.add_db_environment(
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        db_host=db_host
    )

    self.apigateway.add_route(
        path="/users/groups",
        method=HttpMethod.POST,
        lambda_handler=create_user_groups_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/users/groups/{id}",
        method=HttpMethod.PUT,
        lambda_handler=edit_user_groups_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/users/groups/{id}",
        method=HttpMethod.DELETE,
        lambda_handler=delete_user_groups_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/users/groups",
        method=HttpMethod.GET,
        lambda_handler=get_user_groups_lambda._lambda,
    )

    self.apigateway.add_route(
        path="/users/groups/{id}",
        method=HttpMethod.GET,
        lambda_handler=get_user_groups_lambda._lambda,
    )
