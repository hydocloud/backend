''' Stack to manage dns configuration '''

from aws_cdk import (
    core,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_apigateway as apigw,
)


class DnsStack(core.Stack):
    ''' Class that implement dns management '''
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.domain_name = "hydo.cloud"
        self.hydo_cloud_zone = route53.HostedZone.from_lookup(
            self, "Hydo", domain_name=self.domain_name
        )

    def add_api_gateway_record(self, name: str, api: apigw):
        ''' Add A record for api gw custom domain name '''
        route53.ARecord(
            self,
            name,
            zone=self.hydo_cloud_zone,
            target=route53.RecordTarget.from_alias(targets.ApiGateway(api)),
            record_name=name,
        )

    def add_api_gateway_v2_record(self, name: str, api):
        ''' Add A record for http api gw custom domain name '''
        route53.ARecord(
            self,
            name,
            zone=self.hydo_cloud_zone,
            target=route53.RecordTarget.from_alias(targets.ApiGatewayv2Domain(api)),
            record_name=name,
        )

    def get_domain_name(self) -> str:
        ''' Return domain name '''
        return self.domain_name

    def get_hosted_zone(self) -> route53.HostedZone:
        ''' Return hosted zone id '''
        return self.hydo_cloud_zone
