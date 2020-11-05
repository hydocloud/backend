#!/usr/bin/env python3

from aws_cdk import core
from aws_cdk.core import Environment

from infrastructure_stack import InfrastructureStack


app = core.App()
InfrastructureStack(app, "infrastructure", env=Environment(account="457469494885", region="eu-west-1"))

app.synth()
