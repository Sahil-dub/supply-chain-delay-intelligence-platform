from __future__ import annotations

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.exceptions import AnalyticsServiceError
from api.services.query_helpers import fetch_all, fetch_one

LOGGER = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, session: Session):
        self.session = session

    def get_overview_kpis(self) -> dict[str, object]:
        return self._fetch_one_or_error("SELECT * FROM vw_delivery_performance_overview")

    def get_delay_trends(self) -> list[dict[str, object]]:
        return self._fetch_all(
            """
            SELECT
                delivery_month,
                total_shipments,
                delivered_shipments,
                delayed_shipments,
                delay_rate_pct,
                avg_delay_days,
                total_order_value_eur
            FROM vw_monthly_delay_trends
            ORDER BY delivery_month
            """
        )

    def get_top_delay_reasons(self, limit: int = 10) -> list[dict[str, object]]:
        return self._fetch_all(
            """
            SELECT
                delay_reason,
                delayed_shipments,
                share_of_delays_pct,
                avg_delay_days
            FROM vw_top_delay_reasons
            ORDER BY delayed_shipments DESC
            LIMIT :limit
            """,
            {"limit": limit},
        )

    def get_supplier_performance(self, limit: int = 25) -> list[dict[str, object]]:
        return self._fetch_all(
            """
            SELECT
                supplier_id,
                supplier_name,
                supplier_country,
                reliability_band,
                reliability_score,
                delivered_shipments,
                delayed_shipments,
                on_time_delivery_rate_pct,
                avg_delay_days,
                supplier_reliability_score_pct
            FROM vw_supplier_reliability_ranking
            ORDER BY supplier_reliability_score_pct ASC, delayed_shipments DESC
            LIMIT :limit
            """,
            {"limit": limit},
        )

    def get_warehouse_performance(self) -> list[dict[str, object]]:
        return self._fetch_all(
            """
            SELECT
                warehouse_id,
                warehouse_name,
                warehouse_city,
                overload_risk_band,
                total_shipments,
                delayed_shipments,
                delay_rate_pct,
                overload_flag_rate_pct,
                avg_delay_days
            FROM vw_warehouse_bottlenecks
            ORDER BY delay_rate_pct DESC, overload_flag_rate_pct DESC
            """
        )

    def get_inventory_risk(self, limit: int = 50) -> list[dict[str, object]]:
        return self._fetch_all(
            """
            SELECT
                product_id,
                product_name,
                category,
                warehouse_id,
                warehouse_name,
                on_hand_units,
                reserved_units,
                available_units,
                reorder_point,
                stock_coverage_ratio,
                stockout_risk_level
            FROM vw_inventory_stockout_risk
            WHERE stockout_risk_level IN ('high', 'medium')
            ORDER BY
                CASE stockout_risk_level
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    ELSE 3
                END,
                stock_coverage_ratio ASC,
                available_units ASC
            LIMIT :limit
            """,
            {"limit": limit},
        )

    def get_high_risk_shipments(self, limit: int = 50) -> list[dict[str, object]]:
        return self._fetch_all(
            """
            SELECT
                shipment_id,
                order_id,
                promised_delivery_date,
                actual_delivery_date,
                shipment_status,
                supplier_name,
                warehouse_name,
                product_name,
                priority,
                order_value_eur,
                delay_days,
                delay_reason,
                stockout_flag,
                warehouse_overload_flag,
                risk_level
            FROM vw_high_risk_shipments
            ORDER BY
                CASE risk_level
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END,
                delay_days DESC NULLS LAST,
                order_value_eur DESC
            LIMIT :limit
            """,
            {"limit": limit},
        )

    def _fetch_one_or_error(self, sql: str, parameters: dict[str, object] | None = None) -> dict[str, object]:
        try:
            row = fetch_one(self.session, sql, parameters)
        except SQLAlchemyError as exc:
            LOGGER.exception("Analytics query failed")
            raise AnalyticsServiceError("Analytics query failed") from exc

        if row is None:
            raise AnalyticsServiceError("Analytics query returned no data")
        return row

    def _fetch_all(self, sql: str, parameters: dict[str, object] | None = None) -> list[dict[str, object]]:
        try:
            return fetch_all(self.session, sql, parameters)
        except SQLAlchemyError as exc:
            LOGGER.exception("Analytics query failed")
            raise AnalyticsServiceError("Analytics query failed") from exc

