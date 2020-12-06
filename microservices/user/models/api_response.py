from pydantic import BaseModel


class LambdaResponse(BaseModel):
    statusCode: int
    body: dict
