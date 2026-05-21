from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    database_connected: bool


class OverviewKpiResponse(BaseModel):
    total_shipments: int
    delivered_shipments: int
    in_transit_shipments: int
    delayed_shipments: int
    on_time_delivery_rate_pct: float | None
    delayed_delivery_rate_pct: float | None
    avg_delivery_variance_days: float | None
    avg_delay_days: float | None
    total_order_value_eur: Decimal | None


class DelayTrendResponse(BaseModel):
    delivery_month: date
    total_shipments: int
    delivered_shipments: int
    delayed_shipments: int
    delay_rate_pct: float | None
    avg_delay_days: float | None
    total_order_value_eur: Decimal | None


class DelayReasonResponse(BaseModel):
    delay_reason: str | None
    delayed_shipments: int
    share_of_delays_pct: float | None
    avg_delay_days: float | None


class SupplierPerformanceResponse(BaseModel):
    supplier_id: str
    supplier_name: str
    supplier_country: str
    reliability_band: str
    reliability_score: float
    delivered_shipments: int
    delayed_shipments: int
    on_time_delivery_rate_pct: float | None
    avg_delay_days: float | None
    supplier_reliability_score_pct: float | None


class WarehousePerformanceResponse(BaseModel):
    warehouse_id: str
    warehouse_name: str
    warehouse_city: str
    overload_risk_band: str
    total_shipments: int
    delayed_shipments: int
    delay_rate_pct: float | None
    overload_flag_rate_pct: float | None
    avg_delay_days: float | None


class InventoryRiskResponse(BaseModel):
    product_id: str
    product_name: str
    category: str
    warehouse_id: str
    warehouse_name: str
    on_hand_units: int
    reserved_units: int
    available_units: int
    reorder_point: int
    stock_coverage_ratio: float | None
    stockout_risk_level: str


class HighRiskShipmentResponse(BaseModel):
    shipment_id: str
    order_id: str
    promised_delivery_date: date | None
    actual_delivery_date: date | None
    shipment_status: str
    supplier_name: str
    warehouse_name: str
    product_name: str
    priority: str
    order_value_eur: Decimal | None
    delay_days: int | None
    delay_reason: str | None
    stockout_flag: bool
    warehouse_overload_flag: bool
    risk_level: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"detail": "Analytics query failed"}})

    detail: str

