from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_rds as rds,
    aws_route53 as route53,
    aws_certificatemanager as certificate_manager,
    aws_iam as iam,
    aws_sqs as sqs,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from utils.prefix import domain_specific, env_specific
from models.apigateway import Apigateway
from models._lambda import Lambda
import os
import pathlib
import subprocess
from shutil import copyfile, copytree
from hydo import user_group, devices, secrets, authorizations

LAMBDA_HANDLER = "app.lambda_handler"


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

        self.create_user_group_queue = sqs.Queue(
            self, "CreateUserGroupQueue", queue_name="create-user-group"
        )

        self.create_device_group_queue = sqs.Queue(
            self, "CreateDeviceGroupQueue", queue_name="create-device-group"
        )

        self.create_authorization_device_queue = sqs.Queue(
            self,
            "CreateAuthorizationDeviceQueue",
            queue_name="create-authorization-device",
        )
        organzations_db_name = "organizations"
        organzations_db_user = "loginService"
        organzations_db_password = "ciaociao"
        # The code that defines your stack goes here
        create_organization_lambda = Lambda(
            current_stack=self,
            db_name=organzations_db_name,
            db_user=organzations_db_user,
            db_password=organzations_db_password,
            db_host=rds.db_instance_endpoint_address,
            code_path=f"{self.current_path}/organization/create_organization",
        )
        create_organization_lambda.set_function(name="CreateOrganization")

        # create_organization_lambda = _lambda.Function(
        #     self,
        #     "CreateOrganization",
        #     runtime=_lambda.Runtime.PYTHON_3_8,
        #     code=_lambda.Code.asset(
        #         "{}/organization/create_organization".format(self.current_path)
        #     ),
        #     handler=LAMBDA_HANDLER,
        #     tracing=_lambda.Tracing.ACTIVE,
        #     environment={
        #         "DB_PORT": rds.db_instance_endpoint_port,
        #         "DB_HOST": rds.db_instance_endpoint_address,
        #         "DB_NAME": "organizations",
        #         "DB_ENGINE": "postgresql",
        #         "DB_USER": "loginService",
        #         "DB_PASSWORD": "ciaociao",
        #         "QUEUE_URLS": f'["{self.create_user_group_queue.queue_url}","{self.create_device_group_queue.queue_url}"]',
        #     },
        #     layers=[
        #         self.create_dependencies_layer(
        #             "test", "CreateOrganization", "/organization/create_organization"
        #         ),
        #         self.create_model_layer("test2", "CreateOrganization", "/organization"),
        #     ],
        # )

        # self.create_user_group_queue.grant_send_messages(
        #     grantee=create_organization_lambda
        # )

        # self.create_device_group_queue.grant_send_messages(
        #     grantee=create_organization_lambda
        # )

        edit_organization_lambda = _lambda.Function(
            self,
            "EditOrganization",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset(
                "{}/organization/edit_organization".format(self.current_path)
            ),
            handler=LAMBDA_HANDLER,
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "DB_PORT": rds.db_instance_endpoint_port,
                "DB_HOST": rds.db_instance_endpoint_address,
                "DB_NAME": "organizations",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "ciaociao",
            },
            layers=[
                self.create_dependencies_layer(
                    "EditOrganizationLibraries",
                    "EditOrganization",
                    "/organization/edit_organization",
                ),
                self.create_model_layer(
                    "EditOrganizationModels", "EditOrganization", "/organization"
                ),
            ],
        )

        delete_organization_lambda = _lambda.Function(
            self,
            "DeleteOrganization",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset(
                "{}/organization/delete_organization".format(self.current_path)
            ),
            handler=LAMBDA_HANDLER,
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "DB_PORT": rds.db_instance_endpoint_port,
                "DB_HOST": rds.db_instance_endpoint_address,
                "DB_NAME": "organizations",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "ciaociao",
            },
            layers=[
                self.create_dependencies_layer(
                    "DeleteOrganizationLibraries",
                    "DeleteOrganization",
                    "/organization/delete_organization",
                ),
                self.create_model_layer(
                    "DeleteOrganizationModels",
                    "DeleteOrganization",
                    "/organization",
                ),
            ],
        )

        get_organizations_lambda = _lambda.Function(
            self,
            "GetOrganizations",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset(
                "{}/organization/get_organizations".format(self.current_path)
            ),
            handler=LAMBDA_HANDLER,
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "DB_PORT": rds.db_instance_endpoint_port,
                "DB_HOST": rds.db_instance_endpoint_address,
                "DB_NAME": "organizations",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "ciaociao",
            },
            layers=[
                self.create_dependencies_layer(
                    "GetOrganizationsLibraries",
                    "GetOrganizations",
                    "/organization/get_organizations",
                ),
                self.create_model_layer(
                    "GetOrganizationsModels", "GetOrganizations", "/organization"
                ),
            ],
        )

        authorizer_lambda = _lambda.Function(
            self,
            "Authorizer",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset(
                "{}/authorizer/authorizer".format(self.current_path)
            ),
            handler=LAMBDA_HANDLER,
            tracing=_lambda.Tracing.ACTIVE,
            environment={"JWT_SECRET": "secret"},
            layers=[
                self.create_dependencies_layer(
                    "Authorizer", "Authorizer", "/authorizer/authorizer"
                )
            ],
        )

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
            lambda_handler=create_organization_lambda,
        )

        self.apigateway.add_route(
            path="/organizations/{id}",
            method=HttpMethod.PUT,
            lambda_handler=edit_organization_lambda,
        )

        self.apigateway.add_route(
            path="/organizations/{id}",
            method=HttpMethod.DELETE,
            lambda_handler=delete_organization_lambda,
        )

        self.apigateway.add_route(
            path="/organizations",
            method=HttpMethod.GET,
            lambda_handler=get_organizations_lambda,
        )

        self.apigateway.add_route(
            path="/organizations/{id}",
            method=HttpMethod.GET,
            lambda_handler=get_organizations_lambda,
        )

        self.apigateway.set_lambda_authorizer(
            type="REQUEST",
            identity_source="$request.header.Authorization",
            object_name="LambdaAuthorizer",
            authorizer_name="LambdaAuthorizer",
            lambda_arn=authorizer_lambda.function_arn,
            region=self.region,
        )

        authorizer_lambda.add_permission(
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

    def create_dependencies_layer(
        self, project_name, function_name, folder_name: str
    ) -> _lambda.LayerVersion:
        requirements_file = "{}{}/requirements.txt".format(
            self.current_path, folder_name
        )
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

    def create_model_layer(
        self, project_name, function_name, folder_name: str
    ) -> _lambda.LayerVersion:
        base_path = self.current_path + folder_name
        output_dir = ".lambda_dependencies/" + function_name + "/commodities"
        os.makedirs(output_dir + "/python", exist_ok=True)
        copyfile(
            "{}/database.py".format(base_path),
            f"{output_dir}/python/database.py",
        )
        copytree(
            "{}/models".format(base_path),
            f"{output_dir}/python/models/",
            dirs_exist_ok=True,
        )
        copytree(
            "{}/microservices/psycopg2".format(str(pathlib.Path().absolute())),
            f"{output_dir}/python/psycopg2/",
            dirs_exist_ok=True,
        )

        return _lambda.LayerVersion(
            self,
            project_name + "-" + function_name + "-dependencies",
            code=_lambda.Code.from_asset(output_dir),
        )
