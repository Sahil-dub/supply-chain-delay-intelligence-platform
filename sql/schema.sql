-- Phase 3: PostgreSQL schema for the Supply Chain Delay Intelligence Platform.
-- This schema stores the generated operational CSV data from data/raw/.

DROP TABLE IF EXISTS shipments CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;

CREATE TABLE suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(120) NOT NULL,
    country VARCHAR(80) NOT NULL,
    reliability_score NUMERIC(5, 3) NOT NULL CHECK (reliability_score BETWEEN 0 AND 1),
    reliability_band VARCHAR(20) NOT NULL CHECK (reliability_band IN ('high', 'medium', 'low')),
    standard_lead_time_days INTEGER NOT NULL CHECK (standard_lead_time_days > 0),
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE suppliers IS 'Supplier master data used to analyze supplier reliability and delay risk.';
COMMENT ON COLUMN suppliers.reliability_score IS 'Synthetic baseline reliability score; lower scores increase probability of shipment delay.';
COMMENT ON COLUMN suppliers.reliability_band IS 'Business-friendly grouping of supplier reliability: high, medium, or low.';
COMMENT ON COLUMN suppliers.standard_lead_time_days IS 'Typical supplier lead time used when generating promised delivery dates.';

CREATE TABLE warehouses (
    warehouse_id VARCHAR(20) PRIMARY KEY,
    warehouse_name VARCHAR(120) NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(20) NOT NULL,
    daily_capacity_units INTEGER NOT NULL CHECK (daily_capacity_units > 0),
    storage_capacity_units INTEGER NOT NULL CHECK (storage_capacity_units > 0),
    overload_risk_band VARCHAR(20) NOT NULL CHECK (overload_risk_band IN ('low', 'medium', 'high'))
);

COMMENT ON TABLE warehouses IS 'Warehouse master data used to analyze fulfillment bottlenecks and capacity pressure.';
COMMENT ON COLUMN warehouses.daily_capacity_units IS 'Expected daily outbound capacity before warehouse delay risk increases.';
COMMENT ON COLUMN warehouses.storage_capacity_units IS 'Approximate storage capacity for inventory planning context.';
COMMENT ON COLUMN warehouses.overload_risk_band IS 'Synthetic risk band for warehouse capacity bottlenecks.';

CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(120) NOT NULL,
    category VARCHAR(80) NOT NULL,
    primary_supplier_id VARCHAR(20) NOT NULL REFERENCES suppliers(supplier_id),
    unit_cost_eur NUMERIC(12, 2) NOT NULL CHECK (unit_cost_eur >= 0),
    reorder_point INTEGER NOT NULL CHECK (reorder_point >= 0),
    hazmat_flag BOOLEAN NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE products IS 'Product master data used for category-level delay and inventory analysis.';
COMMENT ON COLUMN products.primary_supplier_id IS 'Main supplier for the product; links products to supplier reliability.';
COMMENT ON COLUMN products.unit_cost_eur IS 'Synthetic unit cost in euros used to estimate order value.';
COMMENT ON COLUMN products.reorder_point IS 'Minimum target inventory level before stockout risk should be reviewed.';
COMMENT ON COLUMN products.hazmat_flag IS 'Indicates whether a product may require special handling.';

CREATE TABLE inventory (
    inventory_id VARCHAR(60) PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    warehouse_id VARCHAR(20) NOT NULL REFERENCES warehouses(warehouse_id),
    on_hand_units INTEGER NOT NULL CHECK (on_hand_units >= 0),
    reserved_units INTEGER NOT NULL CHECK (reserved_units >= 0),
    reorder_point INTEGER NOT NULL CHECK (reorder_point >= 0),
    last_stock_count_date DATE NOT NULL,
    CONSTRAINT inventory_product_warehouse_unique UNIQUE (product_id, warehouse_id),
    CONSTRAINT inventory_reserved_not_above_on_hand CHECK (reserved_units <= on_hand_units)
);

COMMENT ON TABLE inventory IS 'Inventory snapshot by product and warehouse for stockout-risk analysis.';
COMMENT ON COLUMN inventory.on_hand_units IS 'Units physically available at the warehouse at the time of the snapshot.';
COMMENT ON COLUMN inventory.reserved_units IS 'Units already committed to demand and not freely available.';
COMMENT ON COLUMN inventory.reorder_point IS 'Inventory threshold used to identify replenishment or stockout risk.';
COMMENT ON COLUMN inventory.last_stock_count_date IS 'Date of the most recent stock count used for inventory freshness context.';

CREATE TABLE orders (
    order_id VARCHAR(30) PRIMARY KEY,
    customer_region VARCHAR(40) NOT NULL,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    supplier_id VARCHAR(20) NOT NULL REFERENCES suppliers(supplier_id),
    warehouse_id VARCHAR(20) NOT NULL REFERENCES warehouses(warehouse_id),
    order_date DATE NOT NULL,
    order_quantity INTEGER NOT NULL CHECK (order_quantity > 0),
    order_value_eur NUMERIC(14, 2) NOT NULL CHECK (order_value_eur >= 0),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('standard', 'expedited', 'critical')),
    order_status VARCHAR(20) NOT NULL CHECK (order_status IN ('fulfilled', 'open'))
);

COMMENT ON TABLE orders IS 'Customer demand records used to connect product, supplier, warehouse, and shipment performance.';
COMMENT ON COLUMN orders.customer_region IS 'Customer delivery region used for geographic demand and delay analysis.';
COMMENT ON COLUMN orders.order_quantity IS 'Units ordered; high quantities can create inventory pressure.';
COMMENT ON COLUMN orders.order_value_eur IS 'Synthetic monetary value of the order in euros.';
COMMENT ON COLUMN orders.priority IS 'Operational priority level that can be analyzed against delay outcomes.';
COMMENT ON COLUMN orders.order_status IS 'Order fulfillment status, usually fulfilled unless the shipment is still in transit.';

CREATE TABLE shipments (
    shipment_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL UNIQUE REFERENCES orders(order_id),
    supplier_id VARCHAR(20) NOT NULL REFERENCES suppliers(supplier_id),
    warehouse_id VARCHAR(20) NOT NULL REFERENCES warehouses(warehouse_id),
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    ship_date DATE NOT NULL,
    promised_delivery_date DATE,
    actual_delivery_date DATE,
    delay_days INTEGER,
    is_delayed BOOLEAN,
    delay_reason VARCHAR(80),
    carrier VARCHAR(80) NOT NULL,
    shipment_status VARCHAR(20) NOT NULL CHECK (shipment_status IN ('delivered', 'in_transit')),
    stockout_flag BOOLEAN NOT NULL,
    warehouse_overload_flag BOOLEAN NOT NULL,
    CONSTRAINT delivered_shipments_have_actual_date CHECK (
        shipment_status <> 'delivered' OR actual_delivery_date IS NOT NULL
    ),
    CONSTRAINT in_transit_shipments_have_no_delay_label CHECK (
        shipment_status <> 'in_transit' OR (actual_delivery_date IS NULL AND delay_days IS NULL AND is_delayed IS NULL)
    )
);

COMMENT ON TABLE shipments IS 'Shipment execution records used for delay KPIs, bottleneck analysis, and future prediction labels.';
COMMENT ON COLUMN shipments.promised_delivery_date IS 'Date promised to the customer or internal stakeholder; missing values represent raw data quality issues.';
COMMENT ON COLUMN shipments.actual_delivery_date IS 'Actual delivery date when shipment has been delivered.';
COMMENT ON COLUMN shipments.delay_days IS 'Actual delivery date minus promised delivery date. Positive values mean late delivery.';
COMMENT ON COLUMN shipments.is_delayed IS 'Boolean delay label used for KPIs and future delay-risk modeling.';
COMMENT ON COLUMN shipments.delay_reason IS 'Main synthetic operational reason for delayed delivered shipments.';
COMMENT ON COLUMN shipments.stockout_flag IS 'Whether the order quantity exceeded available inventory at generation time.';
COMMENT ON COLUMN shipments.warehouse_overload_flag IS 'Whether the fulfillment warehouse was under simulated capacity pressure.';

