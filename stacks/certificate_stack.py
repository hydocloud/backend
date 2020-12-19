""" Stack to deploy https certificate """

from aws_cdk import (
    core,
    aws_route53 as route53,
    aws_certificatemanager as certificate_manager,
)


class CertificateStack(core.Stack):
    """
    Certificate stack with init method to get data from actual route zone
    and method to issue new certificate and validate
    """

    def __init__(
        self, scope: core.Construct, id: str, dns_stack: route53, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.hosted_zone = dns_stack.get_hosted_zone()
        self.domain_name = dns_stack.get_domain_name()

    def issue_certificate(
        self, name: str, record_name: str
    ) -> certificate_manager.Certificate:
        """ Issue and validate new https certficate """
        return certificate_manager.Certificate(
            self,
            name,
            domain_name="{}.{}".format(record_name, self.domain_name),
            validation=certificate_manager.CertificateValidation.from_dns(
                self.hosted_zone
            ),
        )
