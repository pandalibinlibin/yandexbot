from influxdb_client import InfluxDBClient
from datetime import datetime
from typing import List, Dict, Any
from .models import SalesMetrics


class InfluxDBService:
    """InfluxDB service for time series data operations"""

    def __init__(self):
        self.client = InfluxDBClient(
            url="http://influxdb:8086",
            token="yandexbot-token",
            org="yandexbot",
        )
        self.bucket = "sales_metrics"

    def write_sales_metrics(self, metrics: SalesMetrics) -> None:
        """Write sales metrics to InfluxDB"""
        point = {
            "measurement": "sales_metrics",
            "tags": {
                "product_id": metrics.product_id,
                "category": metrics.category,
            },
            "fields": {
                "impressions": metrics.impressions,
                "clicks": metrics.clicks,
                "add_to_cart": metrics.add_to_cart,
                "orders": metrics.orders,
                "ctr": metrics.ctr,
                "add_to_cart_rate": metrics.add_to_cart_rate,
                "order_rate": metrics.order_rate,
            },
            "time": metrics.timestamp or datetime.utcnow(),
        }

        write_api = self.client.write_api().write(
            bucket=self.bucket,
            record=point,
        )

    def query_sales_metrics(
        self, product_id, str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Query sales metrics from InfluxDB with specific time range"""
        if end_time is None:
            end_time = datetime.utcnow()

        query = f"""
        from(bucket: "{self.bucket}")
        |> range(start: {start_time.isoformat()}Z, stop: {end_time.isoformat()}Z)
        |> filter(fn: (r) => r["_measurement"] == "sales_metrics")
        |> filter(fn: (r) => r["product_id"] == "{product_id}")
        """

        result = self.client.query_api().query(query)

        return self._parse_query_result(result)

    def query_sales_metrics_by_days(
        self, product_id: str, days: int
    ) -> List[Dict[str, Any]]:
        """Query sales metrics for the last N days"""
        from datetime import timedelta

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        return self.query_sales_metrics(product_id, days, start_time, end_time)

    def _parse_query_result(self, result) -> pd.DataFrame:
        """Parse InfluxDB query result to pandas DataFrame"""
        import pandas as pd

        data = []
        for table in result:
            for record in table.records:
                data.append(
                    {
                        "time": record.get_time(),
                        "product_id": record.values.get("product_id"),
                        "category": record.values.get("category"),
                        "field": record.get_field(),
                        "value": record.get_value(),
                    }
                )

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        wide_df = df.pivot(
            index=["time", "product_id", "category"],
            columns="field",
            values="value",
            aggfunc="first",
        ).reset_index()

        wide_df = wide_df.fillna(0)

        return wide_df


influxdb_service = InfluxDBService()
