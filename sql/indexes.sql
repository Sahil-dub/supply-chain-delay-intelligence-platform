-- Phase 3: Indexes for common analytics access patterns.
-- These indexes support supplier, warehouse, inventory, date trend, and delay analysis queries.

CREATE INDEX IF NOT EXISTS idx_products_primary_supplier
    ON products (primary_supplier_id);

CREATE INDEX IF NOT EXISTS idx_inventory_product
    ON inventory (product_id);

CREATE INDEX IF NOT EXISTS idx_inventory_warehouse
    ON inventory (warehouse_id);

CREATE INDEX IF NOT EXISTS idx_inventory_stockout_review
    ON inventory (warehouse_id, product_id, on_hand_units, reorder_point);

CREATE INDEX IF NOT EXISTS idx_orders_order_date
    ON orders (order_date);

CREATE INDEX IF NOT EXISTS idx_orders_supplier
    ON orders (supplier_id);

CREATE INDEX IF NOT EXISTS idx_orders_warehouse
    ON orders (warehouse_id);

CREATE INDEX IF NOT EXISTS idx_orders_product
    ON orders (product_id);

CREATE INDEX IF NOT EXISTS idx_shipments_promised_delivery_date
    ON shipments (promised_delivery_date);

CREATE INDEX IF NOT EXISTS idx_shipments_actual_delivery_date
    ON shipments (actual_delivery_date);

CREATE INDEX IF NOT EXISTS idx_shipments_supplier_delay
    ON shipments (supplier_id, is_delayed);

CREATE INDEX IF NOT EXISTS idx_shipments_warehouse_delay
    ON shipments (warehouse_id, is_delayed);

CREATE INDEX IF NOT EXISTS idx_shipments_product_delay
    ON shipments (product_id, is_delayed);

CREATE INDEX IF NOT EXISTS idx_shipments_delay_reason
    ON shipments (delay_reason)
    WHERE delay_reason IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_shipments_status
    ON shipments (shipment_status);

