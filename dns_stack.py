from aws_cdk import (
    core,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_apigateway as apigw,
    aws_apigatewayv2 as apigw2,
)

class DnsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.domain_name = 'hydo.cloud'
        self.hydo_cloud_zone = route53.HostedZone.from_lookup(
            self,
            'Hydo',
            domain_name=self.domain_name
        )

    def add_api_gateway_record(self, name: str, api: apigw):
        route53.ARecord(
            self,
            name,
            zone=self.hydo_cloud_zone,
            target=route53.RecordTarget.from_alias(targets.ApiGateway(api)),
            record_name=name
        )

    def add_api_gateway_v2_record(self, name: str, api):
        route53.ARecord(
            self,
            name,
            zone=self.hydo_cloud_zone,
            target=route53.RecordTarget.from_alias(targets.ApiGatewayv2Domain(api)),
            record_name=name
        )

    def get_domain_name(self) -> str:
        return self.domain_name

    def get_hosted_zone(self) -> route53.HostedZone:
        return self.hydo_cloud_zone
