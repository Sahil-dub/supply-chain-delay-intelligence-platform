-- Phase 7: Power BI optimized queries.
-- These queries are designed for Power BI import mode or DirectQuery prototypes.
-- Run after sql/kpi_views.sql has created the reusable KPI views.

-- 1. Executive Overview: KPI cards and monthly trend line.
SELECT
    total_shipments,
    delivered_shipments,
    in_transit_shipments,
    delayed_shipments,
    on_time_delivery_rate_pct,
    delayed_delivery_rate_pct,
    avg_delay_days,
    total_order_value_eur
FROM vw_delivery_performance_overview;

SELECT
    delivery_month,
    total_shipments,
    delivered_shipments,
    delayed_shipments,
    delay_rate_pct,
    avg_delay_days,
    total_order_value_eur
FROM vw_monthly_delay_trends
ORDER BY delivery_month;

-- 2. Supplier Analytics: ranking, contribution, and segmentation.
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
    supplier_reliability_score_pct,
    CASE
        WHEN supplier_reliability_score_pct < 55 THEN 'High Risk'
        WHEN supplier_reliability_score_pct < 70 THEN 'Watchlist'
        ELSE 'Stable'
    END AS supplier_risk_segment
FROM vw_supplier_reliability_ranking
WHERE delivered_shipments >= 30
ORDER BY supplier_reliability_score_pct ASC;

SELECT
    supplier_name,
    delayed_shipments,
    ROUND(
        100.0 * delayed_shipments / NULLIF(SUM(delayed_shipments) OVER (), 0),
        2
    ) AS delay_contribution_pct
FROM vw_supplier_reliability_ranking
WHERE delayed_shipments > 0
ORDER BY delayed_shipments DESC;

-- 3. Warehouse Operations: bottlenecks and inventory risk.
SELECT
    warehouse_id,
    warehouse_name,
    warehouse_city,
    warehouse_state,
    overload_risk_band,
    daily_capacity_units,
    total_shipments,
    delayed_shipments,
    delay_rate_pct,
    overload_flag_rate_pct,
    avg_delay_days
FROM vw_warehouse_bottlenecks
ORDER BY delay_rate_pct DESC;

SELECT
    warehouse_id,
    warehouse_name,
    warehouse_city,
    category,
    stockout_risk_level,
    COUNT(*) AS sku_count,
    SUM(on_hand_units) AS total_on_hand_units,
    SUM(reserved_units) AS total_reserved_units,
    SUM(available_units) AS total_available_units,
    ROUND(AVG(stock_coverage_ratio), 2) AS avg_stock_coverage_ratio
FROM vw_inventory_stockout_risk
GROUP BY warehouse_id, warehouse_name, warehouse_city, category, stockout_risk_level
ORDER BY
    warehouse_name,
    CASE stockout_risk_level
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        ELSE 3
    END,
    category;

-- 4. Shipment Risk Monitoring: exception table and delay reasons.
SELECT
    delay_reason,
    delayed_shipments,
    share_of_delays_pct,
    avg_delay_days
FROM vw_top_delay_reasons
ORDER BY delayed_shipments DESC;

SELECT
    shipment_id,
    order_id,
    order_date,
    promised_delivery_date,
    actual_delivery_date,
    shipment_status,
    supplier_name,
    warehouse_name,
    product_name,
    category,
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
    order_value_eur DESC;

-- 5. Common slicer tables for Power BI.
-- Import these as small dimension tables if you want clean slicer controls.
SELECT DISTINCT delivery_month
FROM vw_monthly_delay_trends
ORDER BY delivery_month;

SELECT DISTINCT supplier_country, reliability_band
FROM vw_supplier_reliability_ranking
ORDER BY supplier_country, reliability_band;

SELECT DISTINCT warehouse_city, overload_risk_band
FROM vw_warehouse_bottlenecks
ORDER BY warehouse_city, overload_risk_band;

SELECT DISTINCT category
FROM vw_product_category_delay_analysis
ORDER BY category;

