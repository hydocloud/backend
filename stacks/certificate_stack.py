from aws_cdk import (
    core,
    aws_route53 as route53,
    aws_certificatemanager as certificate_manager,
)


class CertificateStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str, route53: route53, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.hosted_zone = route53.get_hosted_zone()
        self.domain_name = route53.get_domain_name()

    def issue_certificate(
        self, name: str, record_name: str
    ) -> certificate_manager.Certificate:
        return certificate_manager.Certificate(
            self,
            name,
            domain_name="{}.{}".format(record_name, self.domain_name),
            validation=certificate_manager.CertificateValidation.from_dns(
                self.hosted_zone
            ),
        )
