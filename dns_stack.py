from aws_cdk import (
    core,
    aws_route53 as route53
)

class DnsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.hydo_cloud_zone = route53.HostedZone.from_lookup(
            self,
            'Hydo',
            domain_name='hydo.cloud'
        )
