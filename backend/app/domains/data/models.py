from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SalesMetrics(BaseModel):
    """Sales metric data model for product performance tracking"""

    product_id: str
    category: str = "unknown"
    impressions: int = 0
    clicks: int = 0
    add_to_cart: int = 0
    orders: int = 0
    ctr: float = 0.0
    add_to_cart_rate: float = 0.0
    order_rate: float = 0.0
    timestamp: Optional[datetime] = None
