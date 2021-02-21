import os
import pathlib
import subprocess
from aws_cdk import aws_lambda_python
from aws_cdk import aws_lambda
from shutil import copytree, copyfile

DB_PORT = 5432
DB_ENGINE = "postgresql"


class Lambda:
    RUNTIME = aws_lambda.Runtime.PYTHON_3_8
    INDEX = "app.py"
    HANDLER = "lambda_handler"

    def __init__(
        self,
        current_stack,
        db_name: str,
        db_user: str,
        db_password: str,
        db_host: str,
        code_path: str,
    ):
        self.current_stack = current_stack
        self.db_name = db_name
        self.db_password = db_password
        self.db_host = db_host
        self.db_user = db_user
        self.code_path = code_path
        self.base_path = code_path.rsplit("/", 1)

    def set_function(self, name: str):
        self.name = name
        self._lambda = aws_lambda.Function(
            self,
            "GetOrganizations",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.asset(self.code_path),
            handler=Lambda.HANDLER,
            tracing=aws_lambda.Tracing.ACTIVE,
            environment={
                "DB_PORT": DB_PORT,
                "DB_HOST": self.db_host,
                "DB_NAME": self.db_name,
                "DB_ENGINE": DB_ENGINE,
                "DB_USER": self.db_user,
                "DB_PASSWORD": self.db_password,
            },
        )

    def get_function(self):
        return self._lambda

    def get_function_arn(self):
        return self._lambda.function_arn

    def get_function_name(self):
        return self._lambda.function_name

    def add_layer(self, requirements: bool, models: bool):
        layers = []
        if requirements:
            layers.append(self.__create_dependencies_layer())
        if models:
            layers.append(self.__create_model_layer())
        self._lambda.add_layers(layers)

    def __create_dependencies_layer(self):
        requirements_file = f"{self.code_path}/requirements.txt"
        output_dir = ".lambda_dependencies/" + self.name

        if not os.environ.get("SKIP_PIP"):
            subprocess.check_call(
                f"pip install -r {requirements_file} -t {output_dir}/python".split()
            )
        return self._lambda.LayerVersion(
            self.current_stack,
            f"{self.name}-dependencies",
            code=self._lambda.Code.from_asset(output_dir),
        )

    def __create_model_layer(self):
        output_dir = f".lambda_dependencies/{self.name}/commodities"
        os.makedirs(output_dir + "/python", exist_ok=True)
        copyfile(
            "{}/database.py".format(self.base_path),
            f"{output_dir}/python/database.py",
        )
        copytree(
            "{}/models".format(self.base_path),
            f"{output_dir}/python/models/",
            dirs_exist_ok=True,
        )
        copytree(
            f"{str(pathlib.Path().absolute())}/microservices/psycopg2",
            f"{output_dir}/python/psycopg2/",
            dirs_exist_ok=True,
        )

        return self._lambda.LayerVersion(
            self.current_stack,
            f"{self.name}-dependencies",
            code=self._lambda.Code.from_asset(output_dir),
        )


class LambdaPython(Lambda):
    def set_function(self, name: str):
        self._lambda = aws_lambda_python.PythonFunction(
            self.current_stack,
            name,
            runtime=Lambda.RUNTIME,
            entry=self.code_path,
            index=Lambda.INDEX,
            handler=Lambda.HANDLER,
            tracing=aws_lambda.Tracing.ACTIVE,
            environment={
                "DB_PORT": DB_PORT,
                "DB_HOST": self.db_host,
                "DB_NAME": self.db_name,
                "DB_ENGINE": DB_ENGINE,
                "DB_USER": self.db_user,
                "DB_PASSWORD": self.db_password,
            },
        )
