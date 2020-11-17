#!/usr/bin/env python3

from aws_cdk import core
from aws_cdk.core import Environment

from infrastructure_stack import InfrastructureStack
from organization_stack import OrganizationeStack

app = core.App()
infra = InfrastructureStack(app, "infrastructure", env=Environment(account="457469494885", region="eu-west-1"))
OrganizationeStack(app, "organization", infra.api_gateway(), infra.rds(), env=Environment(account="457469494885", region="eu-west-1"))

app.synth()
