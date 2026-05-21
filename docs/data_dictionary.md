# Data Dictionary

This dictionary explains the main Phase 2 synthetic datasets. The PostgreSQL schema will be added in a later phase.

## Suppliers

- `supplier_id`: Unique supplier identifier.
- `supplier_name`: Business-friendly supplier name.
- `country`: Supplier country.
- `reliability_score`: Expected supplier consistency before shipment execution. Lower values create more delay risk.
- `reliability_band`: High, medium, or low reliability grouping.
- `standard_lead_time_days`: Typical supplier lead time.
- `active_flag`: Whether the supplier is active.

## Warehouses

- `warehouse_id`: Unique warehouse identifier.
- `warehouse_name`: Distribution center name.
- `city`: Warehouse city.
- `state`: German federal state abbreviation.
- `daily_capacity_units`: Daily outbound capacity before bottleneck risk increases.
- `storage_capacity_units`: Approximate storage capacity.
- `overload_risk_band`: Low, medium, or high operational bottleneck risk.

## Products

- `product_id`: Unique product identifier.
- `product_name`: Product display name.
- `category`: Product category used for business analysis.
- `primary_supplier_id`: Main supplier for the product.
- `unit_cost_eur`: Unit cost in euros.
- `reorder_point`: Minimum inventory level before stockout risk should be flagged.
- `hazmat_flag`: Indicates whether special handling may be required.

## Inventory

- `inventory_id`: Unique product and warehouse inventory snapshot identifier.
- `product_id`: Product stored at the warehouse.
- `warehouse_id`: Warehouse where inventory is stored.
- `on_hand_units`: Units physically available at the snapshot date.
- `reserved_units`: Units already reserved for orders.
- `reorder_point`: Minimum target stock level.
- `last_stock_count_date`: Date of the latest stock count.

## Orders

- `order_id`: Unique customer order identifier.
- `customer_region`: Customer delivery region.
- `product_id`: Ordered product.
- `supplier_id`: Supplier linked to the ordered product.
- `warehouse_id`: Warehouse responsible for fulfillment.
- `order_date`: Date when the order was placed.
- `order_quantity`: Ordered units.
- `order_value_eur`: Quantity multiplied by product unit cost.
- `priority`: Standard, expedited, or critical.
- `order_status`: Fulfilled or open.

## Shipments

- `shipment_id`: Unique shipment identifier.
- `order_id`: Related order.
- `supplier_id`: Supplier associated with the shipment.
- `warehouse_id`: Fulfillment warehouse.
- `product_id`: Shipped product.
- `ship_date`: Date when the shipment left the warehouse or supplier process.
- `promised_delivery_date`: Date promised to the customer or internal stakeholder.
- `actual_delivery_date`: Actual delivery date when available.
- `delay_days`: Actual delivery date minus promised delivery date.
- `is_delayed`: True when `delay_days` is greater than zero.
- `delay_reason`: Main operational reason for delayed delivered shipments.
- `carrier`: Logistics provider.
- `shipment_status`: Delivered or in transit.
- `stockout_flag`: Whether the order quantity exceeded available inventory.
- `warehouse_overload_flag`: Whether the fulfillment warehouse was under capacity pressure.

