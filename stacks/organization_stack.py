import pathlib
from aws_cdk import (
    core,
    aws_rds as rds,
    aws_route53 as route53,
    aws_certificatemanager as certificate_manager,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_lambda_python as _lambda_python,
)
from aws_cdk.core import Duration
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_lambda import Runtime
from utils.prefix import domain_specific, env_specific
from models.apigateway import Apigateway
from models._lambda import LambdaPython
from hydo import user_group, devices, secrets, authorizations


class OrganizationeStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        rds: rds,
        route53: route53,
        certificate_manager: certificate_manager,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.current_path = str(pathlib.Path().absolute()) + "/microservices"
        self.rds = rds
        self.model_layer = self.__model_layer()

        self.create_user_group_queue = sqs.Queue(
            self,
            "CreateUserGroupQueue",
            queue_name="create-user-group",
            receive_message_wait_time=Duration.seconds(20),
        )

        self.create_device_group_queue = sqs.Queue(
            self,
            "CreateDeviceGroupQueue",
            queue_name="create-device-group",
            receive_message_wait_time=Duration.seconds(20),
        )

        self.create_authorization_device_queue = sqs.Queue(
            self,
            "CreateAuthorizationDeviceQueue",
            queue_name="create-authorization-device",
            receive_message_wait_time=Duration.seconds(20),
        )
        organzations_db_name = "organizations"
        organzations_db_user = "loginService"
        organzations_db_password = "ciaociao"
        # The code that defines your stack goes here
        create_organization_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/organization/src/create_organization",
            name="CreateOrganization",
        )
        create_organization_lambda.set_function()
        create_organization_lambda.add_layer(layer_version=self.model_layer)
        create_organization_lambda.add_db_environment(
            db_user=organzations_db_user,
            db_password=organzations_db_password,
            db_name=organzations_db_name,
            db_host=self.rds.db_instance_endpoint_address,
        )
        create_organization_lambda.add_environment(
            key="QUEUE_URLS",
            value=f'["{self.create_user_group_queue.queue_url}","{self.create_device_group_queue.queue_url}"]',
        )

        self.create_user_group_queue.grant_send_messages(
            grantee=create_organization_lambda._lambda
        )

        self.create_device_group_queue.grant_send_messages(
            grantee=create_organization_lambda._lambda
        )

        edit_organization_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/organization/src/edit_organization",
            name="EditOrganization",
        )
        edit_organization_lambda.set_function()
        edit_organization_lambda.add_layer(layer_version=self.model_layer)
        edit_organization_lambda.add_db_environment(
            db_user=organzations_db_user,
            db_password=organzations_db_password,
            db_name=organzations_db_name,
            db_host=self.rds.db_instance_endpoint_address,
        )

        delete_organization_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/organization/src/delete_organization",
            name="DeleteOrganization",
        )
        delete_organization_lambda.set_function()
        delete_organization_lambda.add_layer(layer_version=self.model_layer)
        delete_organization_lambda.add_db_environment(
            db_user=organzations_db_user,
            db_password=organzations_db_password,
            db_name=organzations_db_name,
            db_host=self.rds.db_instance_endpoint_address,
        )

        get_organizations_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/organization/src/get_organizations",
            name="GetOrganizations",
        )
        get_organizations_lambda.set_function()
        get_organizations_lambda.add_layer(layer_version=self.model_layer)
        get_organizations_lambda.add_db_environment(
            db_user=organzations_db_user,
            db_password=organzations_db_password,
            db_name=organzations_db_name,
            db_host=self.rds.db_instance_endpoint_address,
        )

        authorizer_lambda = LambdaPython(
            current_stack=self,
            code_path=f"{self.current_path}/authorizer/authorizer",
            name="Authorizer",
        )
        authorizer_lambda.set_function()
        authorizer_lambda.add_layer(requirements=True)
        authorizer_lambda.add_environment(key="JWT_SECRET", value="secret")

        #  Api gateway

        certificate = certificate_manager.issue_certificate(
            env_specific("api"), domain_specific("api")
        )

        self.apigateway = Apigateway(
            current_stack=self, object_name="hydo-api", api_name="api-hydo"
        )
        self.apigateway.set_domain_name(
            prefix="api",
            domain_name=route53.get_domain_name(),
            certificate=certificate,
            mapping=True,
        )

        self.apigateway.add_route(
            path="/organizations",
            method=HttpMethod.POST,
            lambda_handler=create_organization_lambda._lambda,
        )

        self.apigateway.add_route(
            path="/organizations/{id}",
            method=HttpMethod.PUT,
            lambda_handler=edit_organization_lambda._lambda,
        )

        self.apigateway.add_route(
            path="/organizations/{id}",
            method=HttpMethod.DELETE,
            lambda_handler=delete_organization_lambda._lambda,
        )

        self.apigateway.add_route(
            path="/organizations",
            method=HttpMethod.GET,
            lambda_handler=get_organizations_lambda._lambda,
        )

        self.apigateway.add_route(
            path="/organizations/{id}",
            method=HttpMethod.GET,
            lambda_handler=get_organizations_lambda._lambda,
        )

        self.apigateway.set_lambda_authorizer(
            type="REQUEST",
            identity_source="$request.header.Authorization",
            object_name="LambdaAuthorizer",
            authorizer_name="LambdaAuthorizer",
            lambda_arn=authorizer_lambda.get_function_arn(),
            region=self.region,
        )

        authorizer_lambda._lambda.add_permission(
            "ApiGWPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=self.apigateway.get_lambda_authorizer().authorizer_credentials_arn,
        )

        route53.add_api_gateway_v2_record(
            domain_specific("api"), self.apigateway.get_domain_name()
        )

        user_group.lambdas(self)
        device_secret_key = secrets.device_symmetric_key(self)
        devices.lambdas(self, device_secret_key)
        authorizations.lambdas(self, device_secret_key)

    def __model_layer(self):
        return _lambda_python.PythonLayerVersion(
            self,
            f'{env_specific("models")}',
            layer_version_name=f'{env_specific("models")}',
            entry=f"{str(pathlib.Path().absolute())}/microservices/shared/",
            compatible_runtimes=[Runtime.PYTHON_3_8],
        )
