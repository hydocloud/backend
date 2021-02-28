import os
import pathlib
import subprocess
from aws_cdk import aws_lambda_python
from aws_cdk import aws_lambda
from shutil import copytree, copyfile
from utils.prefix import env_specific

DB_PORT = 5432
DB_ENGINE = "postgresql"


class Lambda:
    RUNTIME = aws_lambda.Runtime.PYTHON_3_8
    INDEX = "app.py"
    HANDLER = "lambda_handler"

    def __init__(self, current_stack, code_path: str, name: str):
        self.current_stack = current_stack
        self.code_path = code_path
        self.base_path = code_path.rsplit("/", 1)[0]
        self.name = name

    def set_function(self):
        self._lambda = aws_lambda.Function(
            self.current_stack,
            self.name,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.asset(self.code_path),
            handler=Lambda.HANDLER,
            tracing=aws_lambda.Tracing.ACTIVE,
        )

    def get_function(self):
        return self._lambda

    def get_function_arn(self):
        return self._lambda.function_arn

    def get_function_name(self):
        return self._lambda.function_name

    def add_layer(self, requirements: bool = False, models: bool = False, indy: bool = False):
        layers = []
        if requirements:
            layers.append(self.__create_dependencies_layer())
        if models:
            layers.append(self.__create_model_layer())
        if indy:
            layers.append(self.__indy_layer())
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

        return aws_lambda.LayerVersion(
            self.current_stack,
            f"{self.name}-model-dependencies",
            code=aws_lambda.Code.from_asset(output_dir),
        )

    def __indy_layer(self):
        return aws_lambda.LayerVersion(
            self,
            env_specific("indy-sdk-postgres"),
            code=aws_lambda.Code.asset(
                "{}/indysdk-postgres.zip".format(self.base_path)
            ),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8],
        )

    def add_environment(self, key: str, value: str):
        self._lambda.add_environment(key=key, value=value)

    def add_db_environment(self, db_host: str, db_name: str, db_user: str, db_password: str):
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
            environment={
                "DB_PORT": DB_PORT,
                "DB_HOST": self.db_host,
                "DB_NAME": self.db_name,
                "DB_ENGINE": DB_ENGINE,
                "DB_USER": self.db_user,
                "DB_PASSWORD": self.db_password,
            },
        )
