-- Phase 3: Load generated Phase 2 CSV files into PostgreSQL.
-- Run from the project root with psql so the relative data/raw paths resolve correctly.
--
-- Example:
-- psql "postgresql://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay" -f sql/schema.sql
-- psql "postgresql://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay" -f sql/load_data.sql
-- psql "postgresql://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay" -f sql/indexes.sql

\echo 'Clearing existing supply chain tables...'
TRUNCATE TABLE shipments, orders, inventory, products, warehouses, suppliers;

\echo 'Loading suppliers...'
\copy suppliers (supplier_id, supplier_name, country, reliability_score, reliability_band, standard_lead_time_days, active_flag) FROM 'data/raw/suppliers.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading warehouses...'
\copy warehouses (warehouse_id, warehouse_name, city, state, daily_capacity_units, storage_capacity_units, overload_risk_band) FROM 'data/raw/warehouses.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading products...'
\copy products (product_id, product_name, category, primary_supplier_id, unit_cost_eur, reorder_point, hazmat_flag) FROM 'data/raw/products.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading inventory...'
\copy inventory (inventory_id, product_id, warehouse_id, on_hand_units, reserved_units, reorder_point, last_stock_count_date) FROM 'data/raw/inventory.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading orders...'
\copy orders (order_id, customer_region, product_id, supplier_id, warehouse_id, order_date, order_quantity, order_value_eur, priority, order_status) FROM 'data/raw/orders.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading shipments...'
\copy shipments (shipment_id, order_id, supplier_id, warehouse_id, product_id, ship_date, promised_delivery_date, actual_delivery_date, delay_days, is_delayed, delay_reason, carrier, shipment_status, stockout_flag, warehouse_overload_flag) FROM 'data/raw/shipments.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Row count validation:'
SELECT 'suppliers' AS table_name, COUNT(*) AS row_count FROM suppliers
UNION ALL
SELECT 'warehouses', COUNT(*) FROM warehouses
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'shipments', COUNT(*) FROM shipments
ORDER BY table_name;

\echo 'Relationship validation: expected zero invalid references in each row.'
SELECT 'products_missing_supplier' AS check_name, COUNT(*) AS invalid_rows
FROM products p
LEFT JOIN suppliers s ON p.primary_supplier_id = s.supplier_id
WHERE s.supplier_id IS NULL
UNION ALL
SELECT 'inventory_missing_product', COUNT(*)
FROM inventory i
LEFT JOIN products p ON i.product_id = p.product_id
WHERE p.product_id IS NULL
UNION ALL
SELECT 'inventory_missing_warehouse', COUNT(*)
FROM inventory i
LEFT JOIN warehouses w ON i.warehouse_id = w.warehouse_id
WHERE w.warehouse_id IS NULL
UNION ALL
SELECT 'orders_missing_product', COUNT(*)
FROM orders o
LEFT JOIN products p ON o.product_id = p.product_id
WHERE p.product_id IS NULL
UNION ALL
SELECT 'orders_missing_supplier', COUNT(*)
FROM orders o
LEFT JOIN suppliers s ON o.supplier_id = s.supplier_id
WHERE s.supplier_id IS NULL
UNION ALL
SELECT 'orders_missing_warehouse', COUNT(*)
FROM orders o
LEFT JOIN warehouses w ON o.warehouse_id = w.warehouse_id
WHERE w.warehouse_id IS NULL
UNION ALL
SELECT 'shipments_missing_order', COUNT(*)
FROM shipments sh
LEFT JOIN orders o ON sh.order_id = o.order_id
WHERE o.order_id IS NULL
ORDER BY check_name;

\echo 'Operational validation: delay rate and top delay reasons.'
SELECT
    COUNT(*) AS delivered_shipments,
    ROUND(100.0 * AVG(CASE WHEN is_delayed THEN 1 ELSE 0 END), 2) AS delayed_percentage,
    ROUND(AVG(delay_days) FILTER (WHERE is_delayed), 2) AS average_delay_days_for_late_shipments
FROM shipments
WHERE shipment_status = 'delivered';

SELECT
    delay_reason,
    COUNT(*) AS delayed_shipments
FROM shipments
WHERE is_delayed = TRUE
GROUP BY delay_reason
ORDER BY delayed_shipments DESC
LIMIT 5;

\echo 'Data quality validation: raw delay labels that do not match delay_days.'
SELECT
    COUNT(*) AS inconsistent_delay_labels
FROM shipments
WHERE shipment_status = 'delivered'
  AND delay_days IS NOT NULL
  AND is_delayed IS DISTINCT FROM (delay_days > 0);
