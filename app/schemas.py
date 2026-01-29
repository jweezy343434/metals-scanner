"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MetalType(str, Enum):
    """Supported metal types"""
    GOLD = "gold"
    SILVER = "silver"
    ALL = "all"


class ListingResponse(BaseModel):
    """Response model for a listing with computed fields"""
    id: int
    source: str
    external_id: str
    title: str
    price: float
    metal_type: str
    weight_oz: Optional[float]
    weight_extraction_failed: bool
    url: str
    fetched_at: datetime
    spot_value: Optional[float] = None
    spread_percentage: Optional[float] = None

    class Config:
        from_attributes = True


class SpotPriceResponse(BaseModel):
    """Response model for spot prices"""
    metal_type: str
    price_per_oz: float
    fetched_at: datetime
    age_minutes: Optional[int] = None

    class Config:
        from_attributes = True


class ScanResult(BaseModel):
    """Response model for scan operation"""
    success: bool
    listings_found: int
    deals_found: int
    errors: List[str] = []
    started_at: datetime
    completed_at: datetime
    duration_seconds: float


class DealsSummary(BaseModel):
    """Statistics about current deals"""
    total_deals: int
    gold_deals: int
    silver_deals: int
    best_spread_percentage: Optional[float]
    average_spread_percentage: Optional[float]
    total_potential_savings: Optional[float]


class HealthCheck(BaseModel):
    """System health status"""
    status: str
    database: str
    last_scan: Optional[datetime]
    ebay_rate_limit_remaining: Optional[int]
    metals_api_rate_limit_remaining: Optional[int]
    timestamp: datetime


class RateLimitStatus(BaseModel):
    """API quota usage status"""
    api_name: str
    limit: int
    calls_used: int
    calls_remaining: int
    reset_at: datetime
    percentage_used: float


class DealsQuery(BaseModel):
    """Request model for filtering deals"""
    threshold: float = Field(default=0.0, ge=0.0, le=100.0)
    metal_type: Optional[MetalType] = None
    min_weight: Optional[float] = Field(default=None, ge=0.0)
    max_results: Optional[int] = Field(default=100, ge=1, le=1000)

    @validator('min_weight')
    def validate_min_weight(cls, v):
        if v is not None and v <= 0:
            raise ValueError('min_weight must be greater than 0')
        return v


class ScanRequest(BaseModel):
    """Request model for manual scan"""
    metal_types: List[MetalType] = [MetalType.GOLD, MetalType.SILVER]
    max_results_per_search: int = Field(default=100, ge=1, le=100)

    @validator('metal_types')
    def validate_metal_types(cls, v):
        if not v:
            raise ValueError('At least one metal type must be specified')
        # Remove 'all' if present in list
        return [m for m in v if m != MetalType.ALL]


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    api_name: Optional[str] = None
    retry_after: Optional[int] = None
