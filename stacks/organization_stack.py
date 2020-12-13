from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_rds as rds,
    aws_apigatewayv2 as apigw2,
    aws_apigatewayv2_integrations as apigw2_integrations,
    aws_route53 as route53,
    aws_certificatemanager as certificate_manager,
    aws_iam as iam,
    aws_sqs as sqs
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from utils.prefix import domain_specific, env_specific
import os
import pathlib
import subprocess
from shutil import copyfile, copytree
import hydo.user_group as user_group


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

        create_user_group_queue = sqs.Queue(
            self,
            "CreateUserGroupQueue",
            queue_name="create-user-group"
        )

        # The code that defines your stack goes here
        create_organization_lambda = _lambda.Function(
            self,
            "CreateOrganization",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset(
                "{}/organization/create_organization".format(self.current_path)
            ),
            handler="app.lambda_handler",
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "DB_PORT": rds.db_instance_endpoint_port,
                "DB_HOST": rds.db_instance_endpoint_address,
                "DB_NAME": "organizations",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "ciaociao",
                "QUEUE_URL": create_user_group_queue.queue_url
            },
            layers=[
                self.create_dependencies_layer(
                    "test", "CreateOrganization", "/organization/create_organization"
                ),
                self.create_model_layer("test2", "CreateOrganization", "/organization"),
            ],
        )

        edit_organization_lambda = _lambda.Function(
            self,
            "EditOrganization",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset(
                "{}/organization/edit_organization".format(self.current_path)
            ),
            handler="app.lambda_handler",
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
            handler="app.lambda_handler",
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
            handler="app.lambda_handler",
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
            handler="app.lambda_handler",
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

        self.dn = apigw2.DomainName(
            self,
            "http-api-domain-name",
            domain_name="{}.{}".format(
                domain_specific("api"), route53.get_domain_name()
            ),
            certificate=certificate,
        )

        self.http_api = apigw2.HttpApi(
            self, "hydo-api", api_name=env_specific("api-hydo")
        )

        apigw2.HttpApiMapping(
            self, "ApiMapping", api=self.http_api, domain_name=self.dn
        )

        self.http_api.add_routes(
            path="/organizations",
            methods=[HttpMethod.POST],
            integration=apigw2_integrations.LambdaProxyIntegration(
                handler=create_organization_lambda
            ),
        )

        self.http_api.add_routes(
            path="/organizations/{id}",
            methods=[HttpMethod.PUT],
            integration=apigw2_integrations.LambdaProxyIntegration(
                handler=edit_organization_lambda
            ),
        )

        self.http_api.add_routes(
            path="/organizations/{id}",
            methods=[HttpMethod.DELETE],
            integration=apigw2_integrations.LambdaProxyIntegration(
                handler=delete_organization_lambda
            ),
        )

        self.http_api.add_routes(
            path="/organizations",
            methods=[HttpMethod.GET],
            integration=apigw2_integrations.LambdaProxyIntegration(
                handler=get_organizations_lambda
            ),
        )

        self.http_api.add_routes(
            path="/organizations/{id}",
            methods=[HttpMethod.GET],
            integration=apigw2_integrations.LambdaProxyIntegration(
                handler=get_organizations_lambda
            ),
        )

        api_authz = apigw2.CfnAuthorizer(
            self,
            "LambdaAuthorizer",
            api_id=self.http_api.http_api_id,
            authorizer_type="REQUEST",
            identity_source=["$request.header.Authorization"],
            name=env_specific("LambdaAuthorizer"),
            authorizer_payload_format_version="2.0",
            authorizer_uri="arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/{}/invocations".format(
                self.region, authorizer_lambda.function_arn
            ),
        )

        authorizer_lambda.add_permission(
            "ApiGWPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=api_authz.authorizer_credentials_arn,
        )

        route53.add_api_gateway_v2_record(domain_specific("api"), self.dn)

        user_group.lambdas(self)

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
