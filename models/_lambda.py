import os
import pathlib
import subprocess
from aws_cdk import aws_lambda_python
from aws_cdk import aws_lambda
from aws_cdk.core import Duration, AssetHashType
from shutil import copytree, copyfile
from typing import Optional

DB_PORT = 5432
DB_ENGINE = "postgresql"
LAMBDA_POWER_TOOLS_LAYER_ARN = (
    "arn:aws:lambda:eu-west-1:457469494885:layer:aws-lambda-powertools-python-layer:1"
)


class Lambda:
    RUNTIME = aws_lambda.Runtime.PYTHON_3_8
    INDEX = "app.py"
    HANDLER = "lambda_handler"

    def __init__(
        self,
        current_stack,
        code_path: str,
        name: str,
        memory_size: int = 128,
        timeout_seconds: int = 30,
    ):
        self.current_stack = current_stack
        self.code_path = code_path
        self.base_path = code_path.rsplit("/", 1)[0]
        self.name = name
        self.memory_size = memory_size
        self.timeout = Duration.seconds(timeout_seconds)

    def set_function(self):
        self._lambda = aws_lambda.Function(
            self.current_stack,
            self.name,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.asset(self.code_path),
            handler=Lambda.HANDLER,
            tracing=aws_lambda.Tracing.ACTIVE,
            memory_size=self.memory_size,
            timeout=self.timeout,
        )

    def get_function(self):
        return self._lambda

    def get_function_arn(self):
        return self._lambda.function_arn

    def get_function_name(self):
        return self._lambda.function_name

    def add_layer(
        self,
        layer_version: Optional[aws_lambda.LayerVersion] = None,
        requirements: bool = False,
        models: bool = False,
        indy: bool = False,
    ):
        layers = []
        if requirements:
            layers.append(self.__create_dependencies_layer())
        if models:
            layers.append(self.__create_model_layer())
        if indy:
            layers.append(self.__indy_layer())
        if layer_version is not None:
            layers.append(layer_version)
        [self._lambda.add_layers(layer) for layer in layers]

    def __create_dependencies_layer(self):
        requirements_file = f"{self.code_path}/requirements.txt"
        output_dir = ".lambda_dependencies/" + self.name

        if not os.environ.get("SKIP_PIP"):
            subprocess.check_call(
                f"pip install -r {requirements_file} -t {output_dir}/python".split()
            )
        return aws_lambda.LayerVersion(
            self.current_stack,
            f"{self.name}-dependencies",
            code=aws_lambda.Code.from_asset(output_dir),
        )

    def __create_model_layer(self):
        output_dir = f".lambda_dependencies/{self.name}/commodities"
        os.makedirs(output_dir + "/python", exist_ok=True)
        copyfile(
            f"{self.base_path}/database.py",
            f"{output_dir}/python/database.py",
        )
        copytree(
            f"{self.base_path}/models",
            f"{output_dir}/python/models/",
            dirs_exist_ok=True,
        )
        copytree(
            f"{str(pathlib.Path().absolute())}/microservices/psycopg2",
            f"{output_dir}/python/psycopg2/",
            dirs_exist_ok=True,
        )

        return aws_lambda.LayerVersion(
            self.current_stack,
            f"{self.name}-model-dependencies",
            code=aws_lambda.Code.from_asset(output_dir),
        )

    def add_environment(self, key: str, value: str):
        self._lambda.add_environment(key=key, value=value)

    def add_db_environment(
        self, db_host: str, db_name: str, db_user: str, db_password: str
    ):
        self._lambda.add_environment(key="DB_PORT", value=str(DB_PORT))
        self._lambda.add_environment(key="DB_HOST", value=db_host)
        self._lambda.add_environment(key="DB_NAME", value=db_name)
        self._lambda.add_environment(key="DB_ENGINE", value=DB_ENGINE)
        self._lambda.add_environment(key="DB_USER", value=db_user)
        self._lambda.add_environment(key="DB_PASSWORD", value=db_password)


class LambdaPython(Lambda):
    def set_function(self):
        self._lambda = aws_lambda_python.PythonFunction(
            self.current_stack,
            self.name,
            runtime=Lambda.RUNTIME,
            entry=self.code_path,
            index=Lambda.INDEX,
            handler=Lambda.HANDLER,
            tracing=aws_lambda.Tracing.ACTIVE,
            memory_size=self.memory_size,
            timeout=self.timeout,
            asset_hash_type=AssetHashType.SOURCE,
        )
        self._lambda.add_layers(
            aws_lambda.LayerVersion.from_layer_version_arn(
                self.current_stack,
                f"{self.name}-AwsLambdaPowerTools",
                layer_version_arn=LAMBDA_POWER_TOOLS_LAYER_ARN,
            )
        )
