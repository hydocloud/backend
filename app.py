#!/usr/bin/env python3

from aws_cdk import core
from aws_cdk.core import Environment

from login_stack import LoginStack
from organization_stack import OrganizationeStack
from rds_stack import RdsStack

app = core.App()
database = RdsStack(app, "rds", env=Environment(account="457469494885", region="eu-west-1"))
login_stack = LoginStack(app, "login", database.get_rds_instance(), env=Environment(account="457469494885", region="eu-west-1"))
OrganizationeStack(app, "organization", login_stack.api_gateway(), database.get_rds_instance(), env=Environment(account="457469494885", region="eu-west-1"))

app.synth()
