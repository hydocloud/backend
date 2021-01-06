from sqlalchemy.orm.query import Query


class AuthorizationFilter:
    def __init__(
        self,
        query: Query,
        user_id: str = None,
        device_id: int = None,
        authorization_id: int = None,
    ):
        self.device_id = device_id
        self.user_id = user_id
        self.authorization_id = authorization_id
        self.query = query

    def build_filter(self) -> Query:
        if self.authorization_id is not None:
            self.query = self.query.filter_by(id=self.authorization_id)
        if self.user_id is not None:
            self.query = self.query.filter_by(user_id=self.user_id)
        if self.device_id is not None:
            self.query = self.query.filter_by(device_id=self.device_id)

        return self.query
