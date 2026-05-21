-- Phase 5: Reusable PostgreSQL views for BI and reporting.
-- Run after sql/schema.sql, sql/load_data.sql, and sql/indexes.sql.

DROP VIEW IF EXISTS vw_high_risk_shipments;
DROP VIEW IF EXISTS vw_top_delay_reasons;
DROP VIEW IF EXISTS vw_product_category_delay_analysis;
DROP VIEW IF EXISTS vw_monthly_delay_trends;
DROP VIEW IF EXISTS vw_inventory_stockout_risk;
DROP VIEW IF EXISTS vw_warehouse_bottlenecks;
DROP VIEW IF EXISTS vw_supplier_reliability_ranking;
DROP VIEW IF EXISTS vw_delivery_performance_overview;
DROP VIEW IF EXISTS vw_shipment_analytics_base;

-- Business meaning:
-- One enriched shipment-level reporting table that joins shipment execution
-- with order, supplier, warehouse, product, and inventory context.
CREATE VIEW vw_shipment_analytics_base AS
SELECT
    sh.shipment_id,
    sh.order_id,
    o.order_date,
    DATE_TRUNC('month', COALESCE(sh.promised_delivery_date, o.order_date))::DATE AS delivery_month,
    o.customer_region,
    o.order_quantity,
    o.order_value_eur,
    o.priority,
    o.order_status,
    sh.ship_date,
    sh.promised_delivery_date,
    sh.actual_delivery_date,
    sh.delay_days,
    sh.is_delayed,
    sh.delay_reason,
    sh.carrier,
    sh.shipment_status,
    sh.stockout_flag,
    sh.warehouse_overload_flag,
    s.supplier_id,
    s.supplier_name,
    s.country AS supplier_country,
    s.reliability_score,
    s.reliability_band,
    w.warehouse_id,
    w.warehouse_name,
    w.city AS warehouse_city,
    w.state AS warehouse_state,
    w.daily_capacity_units,
    w.overload_risk_band,
    p.product_id,
    p.product_name,
    p.category,
    p.unit_cost_eur,
    i.on_hand_units,
    i.reserved_units,
    i.reorder_point,
    (i.on_hand_units - i.reserved_units) AS available_units,
    CASE
        WHEN i.on_hand_units <= i.reorder_point THEN TRUE
        ELSE FALSE
    END AS below_reorder_point_flag
FROM shipments sh
JOIN orders o
    ON sh.order_id = o.order_id
JOIN suppliers s
    ON sh.supplier_id = s.supplier_id
JOIN warehouses w
    ON sh.warehouse_id = w.warehouse_id
JOIN products p
    ON sh.product_id = p.product_id
LEFT JOIN inventory i
    ON sh.product_id = i.product_id
    AND sh.warehouse_id = i.warehouse_id;

COMMENT ON VIEW vw_shipment_analytics_base IS
'Shipment-level analytics view with order, supplier, warehouse, product, and inventory context.';

-- Business meaning:
-- Executive KPI snapshot for delivery performance.
CREATE VIEW vw_delivery_performance_overview AS
SELECT
    COUNT(*) AS total_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered') AS delivered_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'in_transit') AS in_transit_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE) AS delayed_shipments,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = FALSE)
        / NULLIF(COUNT(*) FILTER (WHERE shipment_status = 'delivered'), 0),
        2
    ) AS on_time_delivery_rate_pct,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE)
        / NULLIF(COUNT(*) FILTER (WHERE shipment_status = 'delivered'), 0),
        2
    ) AS delayed_delivery_rate_pct,
    ROUND(AVG(delay_days) FILTER (WHERE shipment_status = 'delivered'), 2) AS avg_delivery_variance_days,
    ROUND(AVG(delay_days) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE), 2) AS avg_delay_days,
    ROUND(SUM(order_value_eur), 2) AS total_order_value_eur
FROM vw_shipment_analytics_base;

COMMENT ON VIEW vw_delivery_performance_overview IS
'Overall delivery KPI snapshot for operations and BI overview reporting.';

-- Business meaning:
-- Supplier ranking combines actual delivery outcomes with the supplier master reliability score.
CREATE VIEW vw_supplier_reliability_ranking AS
SELECT
    supplier_id,
    supplier_name,
    supplier_country,
    reliability_band,
    reliability_score,
    COUNT(*) AS total_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered') AS delivered_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE) AS delayed_shipments,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = FALSE)
        / NULLIF(COUNT(*) FILTER (WHERE shipment_status = 'delivered'), 0),
        2
    ) AS on_time_delivery_rate_pct,
    ROUND(AVG(delay_days) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE), 2) AS avg_delay_days,
    ROUND(
        (0.7 * (
            COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = FALSE)::NUMERIC
            / NULLIF(COUNT(*) FILTER (WHERE shipment_status = 'delivered'), 0)
        ) + 0.3 * reliability_score) * 100,
        2
    ) AS supplier_reliability_score_pct
FROM vw_shipment_analytics_base
GROUP BY supplier_id, supplier_name, supplier_country, reliability_band, reliability_score;

COMMENT ON VIEW vw_supplier_reliability_ranking IS
'Supplier performance view for ranking suppliers by observed on-time delivery and baseline reliability.';

-- Business meaning:
-- Warehouse view highlights locations with delay pressure and overload signals.
CREATE VIEW vw_warehouse_bottlenecks AS
SELECT
    warehouse_id,
    warehouse_name,
    warehouse_city,
    warehouse_state,
    overload_risk_band,
    daily_capacity_units,
    COUNT(*) AS total_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE) AS delayed_shipments,
    COUNT(*) FILTER (WHERE warehouse_overload_flag = TRUE) AS overload_flagged_shipments,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE)
        / NULLIF(COUNT(*) FILTER (WHERE shipment_status = 'delivered'), 0),
        2
    ) AS delay_rate_pct,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE warehouse_overload_flag = TRUE)
        / NULLIF(COUNT(*), 0),
        2
    ) AS overload_flag_rate_pct,
    ROUND(AVG(delay_days) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE), 2) AS avg_delay_days
FROM vw_shipment_analytics_base
GROUP BY warehouse_id, warehouse_name, warehouse_city, warehouse_state, overload_risk_band, daily_capacity_units;

COMMENT ON VIEW vw_warehouse_bottlenecks IS
'Warehouse bottleneck view for comparing delay rate and simulated capacity pressure by fulfillment location.';

-- Business meaning:
-- Inventory risk view supports stockout and replenishment analysis by product and warehouse.
CREATE VIEW vw_inventory_stockout_risk AS
SELECT
    i.inventory_id,
    i.product_id,
    p.product_name,
    p.category,
    i.warehouse_id,
    w.warehouse_name,
    w.city AS warehouse_city,
    i.on_hand_units,
    i.reserved_units,
    (i.on_hand_units - i.reserved_units) AS available_units,
    i.reorder_point,
    CASE
        WHEN i.on_hand_units <= i.reorder_point THEN 'high'
        WHEN i.on_hand_units <= i.reorder_point * 1.5 THEN 'medium'
        ELSE 'low'
    END AS stockout_risk_level,
    ROUND((i.on_hand_units::NUMERIC / NULLIF(i.reorder_point, 0)), 2) AS stock_coverage_ratio,
    i.last_stock_count_date
FROM inventory i
JOIN products p
    ON i.product_id = p.product_id
JOIN warehouses w
    ON i.warehouse_id = w.warehouse_id;

COMMENT ON VIEW vw_inventory_stockout_risk IS
'Inventory reporting view that classifies stockout risk by product and warehouse.';

-- Business meaning:
-- Monthly trend view supports seasonality and performance monitoring.
CREATE VIEW vw_monthly_delay_trends AS
SELECT
    delivery_month,
    COUNT(*) AS total_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered') AS delivered_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE) AS delayed_shipments,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE)
        / NULLIF(COUNT(*) FILTER (WHERE shipment_status = 'delivered'), 0),
        2
    ) AS delay_rate_pct,
    ROUND(AVG(delay_days) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE), 2) AS avg_delay_days,
    ROUND(SUM(order_value_eur), 2) AS total_order_value_eur
FROM vw_shipment_analytics_base
GROUP BY delivery_month;

COMMENT ON VIEW vw_monthly_delay_trends IS
'Monthly delivery trend view for identifying seasonality and shipment delay spikes.';

-- Business meaning:
-- Category view helps analysts compare product groups that create more delay or stockout pressure.
CREATE VIEW vw_product_category_delay_analysis AS
SELECT
    category,
    COUNT(*) AS total_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered') AS delivered_shipments,
    COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE) AS delayed_shipments,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE)
        / NULLIF(COUNT(*) FILTER (WHERE shipment_status = 'delivered'), 0),
        2
    ) AS delay_rate_pct,
    ROUND(AVG(delay_days) FILTER (WHERE shipment_status = 'delivered' AND is_delayed = TRUE), 2) AS avg_delay_days,
    COUNT(*) FILTER (WHERE stockout_flag = TRUE) AS stockout_flagged_shipments,
    ROUND(SUM(order_value_eur), 2) AS total_order_value_eur
FROM vw_shipment_analytics_base
GROUP BY category;

COMMENT ON VIEW vw_product_category_delay_analysis IS
'Product category delay view for comparing operational risk and order value by category.';

-- Business meaning:
-- Delay reason view explains the most common root causes of late delivered shipments.
CREATE VIEW vw_top_delay_reasons AS
SELECT
    delay_reason,
    COUNT(*) AS delayed_shipments,
    ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) AS share_of_delays_pct,
    ROUND(AVG(delay_days), 2) AS avg_delay_days
FROM vw_shipment_analytics_base
WHERE shipment_status = 'delivered'
  AND is_delayed = TRUE
GROUP BY delay_reason;

COMMENT ON VIEW vw_top_delay_reasons IS
'Delay reason breakdown for identifying the largest operational drivers of late shipments.';

-- Business meaning:
-- High-risk shipments are delivered late or still open with warning signals such as stockout or overload.
CREATE VIEW vw_high_risk_shipments AS
SELECT
    shipment_id,
    order_id,
    order_date,
    promised_delivery_date,
    actual_delivery_date,
    shipment_status,
    supplier_name,
    reliability_band,
    warehouse_name,
    overload_risk_band,
    product_name,
    category,
    priority,
    order_quantity,
    order_value_eur,
    delay_days,
    delay_reason,
    stockout_flag,
    warehouse_overload_flag,
    CASE
        WHEN shipment_status = 'delivered' AND is_delayed = TRUE AND delay_days >= 7 THEN 'critical'
        WHEN shipment_status = 'delivered' AND is_delayed = TRUE THEN 'high'
        WHEN shipment_status = 'in_transit' AND (stockout_flag = TRUE OR warehouse_overload_flag = TRUE) THEN 'medium'
        ELSE 'review'
    END AS risk_level
FROM vw_shipment_analytics_base
WHERE (shipment_status = 'delivered' AND is_delayed = TRUE)
   OR (shipment_status = 'in_transit' AND (stockout_flag = TRUE OR warehouse_overload_flag = TRUE));

COMMENT ON VIEW vw_high_risk_shipments IS
'Shipment exception view for operational review of late deliveries and in-transit risk signals.';

