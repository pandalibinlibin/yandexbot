import httpx
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base.collector import CollectionResult, BaseCollector

logger = logging.getLogger(__name__)


class BaseAPICollector(BaseCollector):
    """Base class for API-based data collectors"""

    def __init__(self, name: str, base_url: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=self._get_default_headers(),
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers"""
        return {
            "User-Agent": "YandexBot/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to the API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Request error: {str(e)}")

    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make GET request"""
        return await self._make_request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make POST request"""
        return await self._make_request("POST", endpoint, **kwargs)

    def validate_config(self) -> bool:
        """Validate the collector configuration"""
        return bool(self.base_url and self.name)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
