from aws_cdk import aws_lambda_python
from aws_cdk import aws_lambda

DB_PORT = 5432
DB_ENGINE = "postgresql"


class LambdaPython:

    RUNTIME = aws_lambda.Runtime.PYTHON_3_8
    INDEX = "app.py"
    HANDLER = "lambda_handler"

    def __init__(
        self,
        db_name: str,
        db_user: str,
        db_password: str,
        db_host: str,
        folder_path: str,
    ):
        self.db_name = db_name
        self.db_password = db_password
        self.db_host = db_host
        self.folder_path = folder_path

    def set_function(self, name: str, code_path: str):
        self._lambda = aws_lambda_python.PythonFunction(
            self,
            name,
            runtime=LambdaPython.RUNTIME,
            entry=code_path,
            index=LambdaPython.INDEX,
            handler=LambdaPython.HANDLER,
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
