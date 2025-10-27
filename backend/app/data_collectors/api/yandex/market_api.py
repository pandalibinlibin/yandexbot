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

    async def collect(self, campaign_id: str, **kwargs) -> CollectionResult:
        """Collect data from Yandex Market API"""
        try:
            collected_data = []

            orders_data = await self._get_orders_stats(campaign_id, **kwargs)
            collected_data.extend(orders_data)

            goods_data = await self._get_goods_stats(campaign_id, **kwargs)
            collected_data.extend(goods_data)

            return CollectionResult(
                success=True,
                data=collected_data,
                collected_at=datetime.utcnow(),
                source=self.name,
                total_records=len(collected_data),
            )
        except Exception as e:
            logger.error(f"Failed to collect data from {self.name}: {str(e)}")
            return CollectionResult(
                success=False,
                data=[],
                error_message=str(e),
                collected_at=datetime.utcnow(),
                source=self.name,
                total_records=0,
            )

    async def _get_orders_stats(
        self, campaign_id: str, date_from: datetime = None, date_to: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get orders statistics from Yandex Market API"""
        if date_from is None:
            date_from = datetime.utcnow() - timedelta(days=7)
        if date_to is None:
            date_to = datetime.utcnow()

        endpoint = f"/v2/campaigns/{campaign_id}/stats/orders"
        params = {
            "dateFrom": date_from.strftime("%Y-%m-%d"),
            "dateTo": date_to.strftime("%Y-%m-%d"),
        }
        logger.debug(f"Fetching orders stats from {endpoint} with params: {params}")
        response = await self.get(endpoint, params=params)

        orders_data = []
        if "result" in response and "orders" in response["result"]:
            for order in response["result"]["orders"]:

                orders_data.append(
                    {
                        "type": "order_stats",
                        "campaign_id": campaign_id,
                        "order_id": order.get("id"),
                        "status": order.get("status"),
                        "created_at": order.get("creationDate"),
                        "total_price": order.get("totalPrice"),
                        "items_count": len(order.get("items", [])),
                        "raw_data": order,
                    }
                )

        return orders_data

    async def _get_goods_stats(
        self, campaign_id: str, shop_skus: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get goods statistics from Yandex Market API"""
        if shop_skus is None:
            shop_skus = await self._get_all_shop_skus(campaign_id)
            if not shop_skus:
                logger.warning("No shop SKUs found for campaign {campaign_id}")
                return []

        all_goods_data = []
        batch_size = 500

        for i in range(0, len(shop_skus), batch_size):
            batch_skus = shop_skus[i : i + batch_size]
            batch_data = await self._get_goods_stats_batch(campaign_id, batch_skus)
            all_goods_data.extend(batch_data)

        return all_goods_data

    async def _get_all_shop_skus(self, campaign_id: str) -> List[str]:
        """Get all Shop SKUs for a campaign"""
        endpoint = f"/v2/campaigns/{campaign_id}/offers"

        all_skus = []
        page_token = None

        while True:
            params = {}
            if page_token:
                params["page_token"] = page_token
            else:
                params["limit"] = 1000

            logger.debug(f"Fetching SKUs from {endpoint} with params: {params}")
            response = await self.post(endpoint, json=params)

            if "result" in response and "offers" in response["result"]:
                offers = response["result"]["offers"]
                if not offers:
                    break

                for offer in offers:
                    if "offerId" in offer:
                        all_skus.append(offer["offerId"])

                if (
                    "pager" in response["result"]
                    and "nextPageToken" in response["result"]["pager"]
                ):
                    page_token = response["result"]["pager"]["nextPageToken"]
                else:
                    break
            else:
                break

        logger.info(f"Found {len(all_skus)} Shop SKUs for campaign {campaign_id}")
        return all_skus

    async def _get_goods_stats_batch(
        self, campaign_id: str, shop_skus: List[str]
    ) -> List[Dict[str, Any]]:
        """Get goods statistics for a batch of SKUs"""
        endpoint = f"/v2/campaigns/{campaign_id}/stats/skus"
        payload = {
            "shopSkus": shop_skus,
        }

        logger.debug(f"Fetching goods stats from {endpoint} for {len(shop_skus)} SKUs")
        response = await self.post(endpoint, json=payload)

        goods_data = []
        if "result" in response and "shopSkus" in response["result"]:
            for sku in response["result"]["shopSkus"]:
                goods_data.append(
                    {
                        "type": "goods_stats",
                        "campaign_id": campaign_id,
                        "shop_sku": sku.get("shopSku"),
                        "market_sku": sku.get("marketSku"),
                        "name": sku.get("name"),
                        "price": sku.get("price"),
                        "category_id": sku.get("categoryId"),
                        "category_name": sku.get("categoryName"),
                        "warehouses": sku.get("warehouses", []),
                        "tariffs": sku.get("tariffs", []),
                        "pictures": sku.get("pictures", []),
                        "raw_data": sku,
                    }
                )

        return goods_data

    async def collect_and_store(self, campaign_id: str, **kwargs) -> CollectionResult:
        """Collect data and store in influxDB"""
        try:
            result = await self.collect(campaign_id, **kwargs)
            if not result.success:
                return result

            stored_count = await self._store_to_influxdb(result.data)

            logger.info(f"Stored {stored_count} records to influxDB")

            return CollectionResult(
                success=True,
                data=result.data,
                collected_at=result.collected_at,
                source=self.name,
                total_records=len(result.data),
                stored_count=stored_count,
            )

        except Exception as e:
            logger.error(f"Failed to collect and store data: {str(e)}")
            return CollectionResult(
                success=False,
                data=[],
                error_message=str(e),
                collected_at=datetime.utcnow(),
                source=self.name,
                total_records=0,
            )

    async def _store_to_influxdb(self, data: List[Dict[str, Any]]) -> int:
        """Store collected data to influxDB"""
        from app.domains.data.services import influxdb_service

        stored_count = 0

        for item in data:
            try:
                if item["type"] == "order_stats":
                    order_time = datetime.fromisoformat(
                        item["created_at"].replace("Z", "+00:00")
                    )

                    metrics = {
                        "product_id": item[
                            "order_id"
                        ],  # Use order_id as product_id for orders
                        "category": "order",
                        "impressions": 0,  # Orders don't have impressions
                        "clicks": 0,  # Orders don't have clicks
                        "add_to_cart": 0,  # Orders don't have add_to_cart
                        "orders": 1,  # This is one order
                        "ctr": 0.0,
                        "add_to_cart_rate": 0.0,
                        "order_rate": 1.0,  # This is a completed order
                        "timestamp": order_time,
                    }

                    influxdb_service.write_sales_metrics(metrics)
                    stored_count += 1
                elif item["type"] == "goods_stats":
                    metrics = {
                        "product_id": item["shop_sku"],
                        "category": item.get("category_name", "unknown"),
                        "impressions": 0,  # Goods stats don't have impressions
                        "clicks": 0,  # Goods stats don't have clicks
                        "add_to_cart": 0,  # Goods stats don't have add_to_cart
                        "orders": 0,  # Goods stats don't have orders
                        "ctr": 0.0,
                        "add_to_cart_rate": 0.0,
                        "order_rate": 0.0,
                        "timestamp": datetime.utcnow(),
                    }

                    influxdb_service.write_sales_metrics(metrics)
                    stored_count += 1

            except Exception as e:
                logger.error(f"Failed to store data to influxDB: {str(e)}")
                continue

        return stored_count
