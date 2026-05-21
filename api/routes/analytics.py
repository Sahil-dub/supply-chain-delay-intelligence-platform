from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_analytics_service
from api.schemas import (
    DelayReasonResponse,
    DelayTrendResponse,
    HighRiskShipmentResponse,
    InventoryRiskResponse,
    OverviewKpiResponse,
    SupplierPerformanceResponse,
    WarehousePerformanceResponse,
)
from api.services.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])


@router.get("/kpis/overview", response_model=OverviewKpiResponse)
def get_overview_kpis(service: AnalyticsService = Depends(get_analytics_service)) -> dict[str, object]:
    return service.get_overview_kpis()


@router.get("/analytics/delay-trends", response_model=list[DelayTrendResponse])
def get_delay_trends(service: AnalyticsService = Depends(get_analytics_service)) -> list[dict[str, object]]:
    return service.get_delay_trends()


@router.get("/analytics/top-delay-reasons", response_model=list[DelayReasonResponse])
def get_top_delay_reasons(
    limit: int = Query(default=10, ge=1, le=50),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[dict[str, object]]:
    return service.get_top_delay_reasons(limit=limit)


@router.get("/analytics/supplier-performance", response_model=list[SupplierPerformanceResponse])
def get_supplier_performance(
    limit: int = Query(default=25, ge=1, le=100),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[dict[str, object]]:
    return service.get_supplier_performance(limit=limit)


@router.get("/analytics/warehouse-performance", response_model=list[WarehousePerformanceResponse])
def get_warehouse_performance(service: AnalyticsService = Depends(get_analytics_service)) -> list[dict[str, object]]:
    return service.get_warehouse_performance()


@router.get("/analytics/inventory-risk", response_model=list[InventoryRiskResponse])
def get_inventory_risk(
    limit: int = Query(default=50, ge=1, le=200),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[dict[str, object]]:
    return service.get_inventory_risk(limit=limit)


@router.get("/analytics/high-risk-shipments", response_model=list[HighRiskShipmentResponse])
def get_high_risk_shipments(
    limit: int = Query(default=50, ge=1, le=200),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[dict[str, object]]:
    return service.get_high_risk_shipments(limit=limit)

