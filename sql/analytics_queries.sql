-- Phase 5: Business-focused analytics queries.
-- Run after sql/kpi_views.sql has created the reusable reporting views.

-- 1. Overall delivery performance
-- Business question: How healthy is the delivery operation overall?
SELECT
    total_shipments,
    delivered_shipments,
    in_transit_shipments,
    delayed_shipments,
    on_time_delivery_rate_pct,
    delayed_delivery_rate_pct,
    avg_delivery_variance_days,
    avg_delay_days,
    total_order_value_eur
FROM vw_delivery_performance_overview;

-- 2. On-time delivery rate by customer region
-- Business question: Are customers in specific regions receiving orders later than others?
SELECT
    customer_region,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered') AS delivered_shipments,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = FALSE)
        / NULLIF(COUNT(*) FILTER (WHERE shipment_status = 'delivered'), 0),
        2
    ) AS on_time_delivery_rate_pct,
    ROUND(AVG(delay_days) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE), 2) AS avg_delay_days
FROM vw_shipment_analytics_base
GROUP BY customer_region
ORDER BY on_time_delivery_rate_pct ASC;

-- 3. Average delay days by shipment priority
-- Business question: Are critical or expedited orders actually performing better?
SELECT
    priority,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered') AS delivered_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE) AS delayed_shipments,
    ROUND(AVG(delay_days) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE), 2) AS avg_delay_days,
    MAX(delay_days) FILTER (WHERE shipment_status = 'delivered') AS max_delay_days
FROM vw_shipment_analytics_base
GROUP BY priority
ORDER BY avg_delay_days DESC NULLS LAST;

-- 4. Supplier reliability ranking
-- Business question: Which suppliers should operations review first?
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
WHERE delivered_shipments >= 50
ORDER BY supplier_reliability_score_pct ASC, delayed_shipments DESC
LIMIT 10;

-- 5. Warehouse bottleneck analysis
-- Business question: Which warehouses show the strongest delay and overload signals?
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
ORDER BY delay_rate_pct DESC, overload_flag_rate_pct DESC;

-- 6. Inventory stockout risk
-- Business question: Which product and warehouse combinations need replenishment attention?
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
LIMIT 25;

-- 7. Monthly delay trends
-- Business question: Are delays increasing during seasonal peaks?
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

-- 8. Product category delay analysis
-- Business question: Which categories create the most delivery and inventory pressure?
SELECT
    category,
    total_shipments,
    delivered_shipments,
    delayed_shipments,
    delay_rate_pct,
    avg_delay_days,
    stockout_flagged_shipments,
    total_order_value_eur
FROM vw_product_category_delay_analysis
ORDER BY delay_rate_pct DESC, stockout_flagged_shipments DESC;

-- 9. Top delay reasons
-- Business question: What are the most common causes of late shipments?
SELECT
    delay_reason,
    delayed_shipments,
    share_of_delays_pct,
    avg_delay_days
FROM vw_top_delay_reasons
ORDER BY delayed_shipments DESC
LIMIT 10;

-- 10. High-risk shipments
-- Business question: Which shipments should an operations analyst review first?
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
LIMIT 50;

-- Validation query: confirm the base analytics view has one row per shipment.
SELECT
    (SELECT COUNT(*) FROM shipments) AS shipment_table_rows,
    (SELECT COUNT(*) FROM vw_shipment_analytics_base) AS analytics_base_rows;

-- Validation query: confirm no duplicate shipment IDs in the analytics base view.
SELECT
    COUNT(*) AS duplicate_shipment_ids
FROM (
    SELECT shipment_id
    FROM vw_shipment_analytics_base
    GROUP BY shipment_id
    HAVING COUNT(*) > 1
) duplicates;

