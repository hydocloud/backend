import logging
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session
from models.devices import Devices


logger = logging.getLogger(__name__)


class DeviceClass:
    def __init__(self, device_id: int):
        self.device_id = device_id

    def get_device(self, connection: Session) -> Optional[Devices]:
        try:
            res = connection.query(Devices).filter_by(id=self.device_id).first()
            return res
        except SQLAlchemyError as err:
            logger.error(err)
        return None

    def get_hmac(self, connection: Session) -> Optional[Devices]:
        try:
            res = connection.query(Devices.id, Devices.hmac_key).filter_by(
                id=self.device_id
            ).first()
            self.hmac_key = res.hmac_key
            return res
        except SQLAlchemyError as err:
            logger.error(err)
        return None
