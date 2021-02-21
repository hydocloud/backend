from typing import Optional
from aws_cdk import (
    aws_apigatewayv2,
    aws_certificatemanager,
    aws_lambda,
    aws_apigatewayv2_integrations,
)
from aws_cdk.aws_apigatewayv2 import HttpMethod
from utils.prefix import env_specific, domain_specific


class Apigateway:
    def __init__(
        self,
        object_name: str,
        api_name: str,
    ):
        self.api_name = api_name
        self.object_name = object_name
        self.http_api = aws_apigatewayv2.HttpApi(
            self, id=object_name, api_name=env_specific(self.api_name)
        )

    def set_domain_name(
        self,
        domain_name: str,
        certificate: aws_certificatemanager.Certificate,
        mapping: bool = False,
        prefix: Optional[str] = "",
        logical_name: Optional[str] = "",
    ):
        self.domain_name = aws_apigatewayv2.DomainName(
            self,
            "http-api-domain-name",
            domain_name="{}.{}".format(
                domain_specific(prefix=prefix, logical_name=logical_name), domain_name
            ),
            certificate=certificate,
        )
        if mapping:
            self.__set_mapping()

    def get_domain_name(self) -> str:
        return self.domain_name

    def __set_mapping(self):
        aws_apigatewayv2.HttpApiMapping(
            self, "ApiMapping", api=self.http_api, domain_name=self.domain_name
        )

    def add_route(
        self, path: str, lambda_handler: aws_lambda.Function, method: HttpMethod
    ):
        self.http_api.add_routes(
            path=path,
            methods=[method],
            integration=aws_apigatewayv2_integrations.LambdaProxyIntegration(
                handler=lambda_handler
            ),
        )

    def set_lambda_authorizer(
        self,
        type: str,
        identity_source: str,
        object_name: str,
        authorizer_name: str,
        lambda_arn: str,
        region: str,
    ):
        authorizer_uri = "arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/{}/invocations".format(
            region, lambda_arn
        )
        self.authorizer = aws_apigatewayv2.CfnAuthorizer(
            self,
            object_name,
            api_id=self.http_api.http_api_id,
            authorizer_type=type,
            identity_source=[identity_source],
            name=env_specific(authorizer_name),
            authorizer_payload_format_version="2.0",
            authorizer_uri=authorizer_uri,
        )

    def get_lambda_authorizer(self) -> aws_apigatewayv2.CfnAuthorizer:
        return self.authorizer
