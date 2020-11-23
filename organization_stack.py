from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_rds as rds,
    aws_apigatewayv2 as apigw2,
    aws_apigatewayv2_integrations as apigw2_integrations,
    aws_route53 as route53,
    aws_certificatemanager as certificate_manager
)
from aws_cdk.core import Duration
from aws_cdk.aws_apigatewayv2 import HttpMethod
from utils.prefix import domain_specific, env_specific
import os
import subprocess
from shutil import copyfile, copytree, rmtree


class OrganizationeStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, rds: rds, route53: route53, certificate_manager: certificate_manager, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        create_organization_lambda = _lambda.Function(
            self,
            "CreateOrganization",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("../microservices/organization/create_organization"),
            handler="app.lambda_handler",
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "DB_PORT": rds.db_instance_endpoint_port,
                "DB_HOST": rds.db_instance_endpoint_address,
                "DB_NAME": "organization",
                "DB_ENGINE": "postgresql",
                "DB_USER": "loginService",
                "DB_PASSWORD": "ciaociao",
            },
            layers=[
                self.create_dependencies_layer(
                    "test", "CreateOrganization", "create_organization"
                ),
                self.create_model_layer(
                    "test2", "CreateOrganization", "create_organization"
                )
            ],
        ) 

        #  Api gateway
        
        certificate = certificate_manager.issue_certificate(env_specific('api'), domain_specific('api'))

        self.dn = apigw2.DomainName(
            self,
            'http-api-domain-name',
            domain_name='{}.{}'.format(domain_specific('api'), route53.get_domain_name()),
            certificate=certificate
        )

        self.http_api = apigw2.HttpApi(
            self,
            'hydo-api',
            api_name=env_specific('api-hydo')       
        )

        apigw2.HttpApiMapping(
            self,
            'ApiMapping',
            api=self.http_api,
            domain_name=self.dn
        )

        self.http_api.add_routes(
            path='/organization',
            methods=[HttpMethod.POST],
            integration=apigw2_integrations.LambdaProxyIntegration(
                handler=create_organization_lambda
            )
        )

    def create_dependencies_layer(self, project_name, function_name, folder_name: str) -> _lambda.LayerVersion:
        requirements_file = "../microservices/organization/{}/requirements.txt".format(
            folder_name
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

    def create_model_layer(self, project_name, function_name, folder_name: str) -> _lambda.LayerVersion:
        base_path = "../microservices/organization"
        output_dir = ".lambda_dependencies/" + function_name + "/commodities"
        os.makedirs(output_dir + "/python", exist_ok=True)
        copyfile('../microservices/organization/database.py', f'{output_dir}/python/database.py')
        copytree('../microservices/organization/models', f'{output_dir}/python/models/', dirs_exist_ok=True)
        
        return _lambda.LayerVersion(
            self,
            project_name + "-" + function_name + "-dependencies",
            code=_lambda.Code.from_asset(output_dir),
        )