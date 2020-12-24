from aws_cdk import (
    core,
    aws_rds as rds,
    aws_ec2 as ec2,
)
from utils.prefix import env_specific


class RdsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Databases
        vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        self.postgres_db = rds.DatabaseInstance(
            self,
            "RDS",
            instance_identifier=env_specific("login"),
            database_name="db1",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_12_4
            ),
            allocated_storage=5,
            vpc=vpc,
            port=5432,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO,
            ),
            removal_policy=core.RemovalPolicy.DESTROY,
            deletion_protection=False,
            credentials=rds.Credentials.from_username("loginService"),
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        self.postgres_db.connections.allow_from_any_ipv4(ec2.Port.tcp(5432))

    def get_rds_instance(self) -> rds.DatabaseInstance:
        return self.postgres_db
