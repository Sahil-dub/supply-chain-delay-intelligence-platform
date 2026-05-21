from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from api.database import check_database_connection
from api.dependencies import get_analytics_service
from api.main import create_app
from api.routes import health


class FakeAnalyticsService:
    def get_overview_kpis(self) -> dict[str, object]:
        return {
            "total_shipments": 12000,
            "delivered_shipments": 11243,
            "in_transit_shipments": 757,
            "delayed_shipments": 4483,
            "on_time_delivery_rate_pct": 60.13,
            "delayed_delivery_rate_pct": 39.87,
            "avg_delivery_variance_days": 0.82,
            "avg_delay_days": 3.03,
            "total_order_value_eur": Decimal("2450000.00"),
        }

    def get_delay_trends(self) -> list[dict[str, object]]:
        return [
            {
                "delivery_month": date(2025, 1, 1),
                "total_shipments": 900,
                "delivered_shipments": 850,
                "delayed_shipments": 280,
                "delay_rate_pct": 32.94,
                "avg_delay_days": 2.7,
                "total_order_value_eur": Decimal("180000.00"),
            }
        ]

    def get_top_delay_reasons(self, limit: int = 10) -> list[dict[str, object]]:
        return [
            {
                "delay_reason": "warehouse_capacity_constraint",
                "delayed_shipments": min(limit, 763),
                "share_of_delays_pct": 17.02,
                "avg_delay_days": 3.2,
            }
        ]

    def get_supplier_performance(self, limit: int = 25) -> list[dict[str, object]]:
        return [
            {
                "supplier_id": "SUP-011",
                "supplier_name": "Saxon Metals",
                "supplier_country": "Germany",
                "reliability_band": "low",
                "reliability_score": 0.61,
                "delivered_shipments": 803,
                "delayed_shipments": min(limit, 394),
                "on_time_delivery_rate_pct": 50.93,
                "avg_delay_days": 3.4,
                "supplier_reliability_score_pct": 53.5,
            }
        ]

    def get_warehouse_performance(self) -> list[dict[str, object]]:
        return [
            {
                "warehouse_id": "WH-001",
                "warehouse_name": "Berlin Distribution Center",
                "warehouse_city": "Berlin",
                "overload_risk_band": "medium",
                "total_shipments": 1500,
                "delayed_shipments": 550,
                "delay_rate_pct": 36.67,
                "overload_flag_rate_pct": 28.4,
                "avg_delay_days": 3.1,
            }
        ]

    def get_inventory_risk(self, limit: int = 50) -> list[dict[str, object]]:
        return [
            {
                "product_id": "PRD-0001",
                "product_name": "Sensor 0001",
                "category": "Electronics",
                "warehouse_id": "WH-001",
                "warehouse_name": "Berlin Distribution Center",
                "on_hand_units": 40,
                "reserved_units": 10,
                "available_units": 30,
                "reorder_point": 100,
                "stock_coverage_ratio": 0.4,
                "stockout_risk_level": "high",
            }
        ][:limit]

    def get_high_risk_shipments(self, limit: int = 50) -> list[dict[str, object]]:
        return [
            {
                "shipment_id": "SHP-000001",
                "order_id": "ORD-000001",
                "promised_delivery_date": date(2025, 3, 13),
                "actual_delivery_date": date(2025, 3, 20),
                "shipment_status": "delivered",
                "supplier_name": "Saxon Metals",
                "warehouse_name": "Berlin Distribution Center",
                "product_name": "Sensor 0001",
                "priority": "critical",
                "order_value_eur": Decimal("12500.00"),
                "delay_days": 7,
                "delay_reason": "supplier_late_dispatch",
                "stockout_flag": False,
                "warehouse_overload_flag": True,
                "risk_level": "critical",
            }
        ][:limit]


def _test_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_analytics_service] = lambda: FakeAnalyticsService()
    return TestClient(app)


def test_health_endpoint_reports_ok_when_database_is_available(monkeypatch) -> None:
    monkeypatch.setattr(health, "check_database_connection", lambda: True)
    client = _test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database_connected"] is True


def test_overview_kpis_endpoint_returns_clean_json() -> None:
    client = _test_client()

    response = client.get("/kpis/overview")

    assert response.status_code == 200
    assert response.json()["total_shipments"] == 12000
    assert response.json()["on_time_delivery_rate_pct"] == 60.13


def test_top_delay_reasons_endpoint_accepts_limit() -> None:
    client = _test_client()

    response = client.get("/analytics/top-delay-reasons?limit=5")

    assert response.status_code == 200
    assert response.json()[0]["delay_reason"] == "warehouse_capacity_constraint"


def test_inventory_risk_endpoint_returns_list() -> None:
    client = _test_client()

    response = client.get("/analytics/inventory-risk")

    assert response.status_code == 200
    assert response.json()[0]["stockout_risk_level"] == "high"


def test_database_health_helper_can_be_imported() -> None:
    assert callable(check_database_connection)

