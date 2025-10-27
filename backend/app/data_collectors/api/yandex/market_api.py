import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from ...base.collector import CollectionResult
from ..base_api import BaseAPICollector

logger = logging.getLogger(__name__)


class YandexMarketAPICollector(BaseAPICollector):
    """Yandex Market Partner API data collector"""

    def __init__(self, token: str, config: Dict[str, Any] = None):
        super().__init__(
            name="yandex_market_api",
            base_url="https://api.partner.market.yandex.ru",
            config=config,
        )
        self.token = token
        self._set_auth()

    @classmethod
    async def create_with_db_token(cls, user_id: str, config: Dict[str, Any] = None):
        """Create collector with token from database"""

        from sqlmodel import Session, select
        from app.core.db import engine
        from app.models import YandexToken

        with Session(engine) as session:
            statement = select(YandexToken).where(YandexToken.owner_id == user_id)
            yandex_token = session.exec(statement).first()

            if not yandex_token:
                raise ValueError(f"Yandex token not found for user {user_id}")

            return cls(token=yandex_token.token, config=config)

    def _set_auth(self):
        """Set authentication headers"""
        self.client.headers.update({"Authorization": f"OAuth {self.token}"})
