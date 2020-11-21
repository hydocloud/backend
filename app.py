#!/usr/bin/env python3

from aws_cdk import core
from aws_cdk.core import Environment

from login_stack import LoginStack
from organization_stack import OrganizationeStack
from rds_stack import RdsStack
from dns_stack import DnsStack
from certificate_stack import CertificateStack

app = core.App()
environment = 'dev'
dns_stack = DnsStack(app, '{}-dns'.format(environment),env=Environment(account='457469494885', region='eu-west-1'))
certificate_stack = CertificateStack(app, '{}-certificate'.format(environment), dns_stack, env=Environment(account='457469494885', region='eu-west-1'))
database = RdsStack(app, '{}-rds'.format(environment), env=Environment(account='457469494885', region='eu-west-1'))
login_stack = LoginStack(app, '{}-login'.format(environment), database.get_rds_instance(), dns_stack, certificate_stack, env=Environment(account='457469494885', region='eu-west-1'))
OrganizationeStack(app, '{}-organization'.format(environment), login_stack.api_gateway(), database.get_rds_instance(), env=Environment(account='457469494885', region='eu-west-1'))

app.synth()
