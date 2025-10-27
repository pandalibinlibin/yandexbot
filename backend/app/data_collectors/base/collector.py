from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class CollectionResult(BaseModel):
    """Data collection result model"""

    success: bool
    data: List[Dict[str, Any]]
    error_message: Optional[str] = None
    collected_at: datetime
    source: str
    total_records: int = 0


class BaseCollector(ABC):
    """Abstract base class for all data collectors"""

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.is_active = True

    @abstractmethod
    async def collect(self, **kwargs) -> CollectionResult:
        """Collect data from the source"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the collector configuration"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get collector status"""
        return {
            "name": self.name,
            "is_active": self.is_active,
            "config_valid": self.validate_config(),
            "last_run": getattr(self, "last_run", None),
        }

    def activate(self):
        """Activate the collector"""
        self.is_active = True

    def deactivate(self):
        """Deactive the collector"""
        self.is_active = False
