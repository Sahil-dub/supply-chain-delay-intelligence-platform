# Phase 7: Power BI Dashboard Design

## What We Built

Phase 7 designs the Power BI reporting layer for the Supply Chain Delay Intelligence Platform.

Created files:

- `dashboards/powerbi_dashboard_plan.md`
- `dashboards/screenshots/.gitkeep`
- `sql/powerbi_dashboard_queries.sql`
- `docs/phase_7_powerbi_dashboard.md`

This phase focuses on BI design quality. It does not create a frontend web dashboard or ML prediction model.

## Dashboard Pages

### 1. Executive Overview

Business purpose:

Give leadership a quick operational health check.

KPIs:

- Total shipments: total shipment volume.
- Delayed shipments: delivered shipments that arrived after promised date.
- On-time delivery rate: share of delivered shipments that arrived on time.
- Average delay days: average lateness among delayed shipments.
- Delay trend over time: monthly view of whether performance is improving or worsening.

Recommended visuals:

- KPI cards.
- Monthly delay rate line chart.
- Delivered vs delayed column chart.
- Top delay reasons bar chart.
- High-risk shipment preview table.

### 2. Supplier Analytics

Business purpose:

Help analysts identify unreliable suppliers and separate supplier problems from warehouse or inventory problems.

Recommended visuals:

- Supplier reliability ranking table.
- Delay contribution by supplier bar chart.
- Reliability score vs on-time delivery rate scatter plot.
- Supplier risk segmentation stacked bar.

Recommended slicers:

- Supplier country.
- Reliability band.
- Product category.
- Delivery month.

### 3. Warehouse Operations

Business purpose:

Help warehouse managers see which locations are overloaded and where inventory shortages may create delays.

Recommended visuals:

- Warehouse delay rate bar chart.
- Overload flag rate bar chart.
- Inventory risk matrix by warehouse and product category.
- High-risk inventory table.

Recommended slicers:

- Warehouse city.
- Product category.
- Stockout risk level.
- Delivery month.

### 4. Shipment Risk Monitoring

Business purpose:

Give operations users an exception list for follow-up.

Recommended visuals:

- High-risk shipments table.
- Delay reasons bar chart.
- Risk level by priority stacked bar.
- KPI cards for critical/high-risk shipment counts.

Recommended slicers:

- Shipment priority.
- Delay reason.
- Risk level.
- Supplier.
- Warehouse.

## Optimized SQL for Power BI

Use:

```text
sql/powerbi_dashboard_queries.sql
```

The file includes dashboard-ready queries for:

- executive overview KPIs
- monthly trends
- supplier ranking
- supplier delay contribution
- warehouse bottlenecks
- inventory risk by warehouse and category
- delay reasons
- high-risk shipment monitoring
- slicer helper tables

## Recommended Power BI Data Model

For a beginner-friendly but professional portfolio version, use import mode with these SQL views:

- `vw_delivery_performance_overview`
- `vw_monthly_delay_trends`
- `vw_supplier_reliability_ranking`
- `vw_warehouse_bottlenecks`
- `vw_inventory_stockout_risk`
- `vw_top_delay_reasons`
- `vw_high_risk_shipments`

If building a more flexible model later, import `vw_shipment_analytics_base` as the central fact-style table and create dimension tables for suppliers, warehouses, products, and dates.

## Theme Suggestions

Use a clean operations dashboard theme:

- Background: very light grey.
- Main text: dark grey.
- Positive KPIs: green.
- Warning states: amber.
- Critical exceptions: red.
- Main chart accent: blue.

Avoid using too many colors at once. The dashboard should feel like an operational control room, not a marketing page.

## Stakeholder Usage

Operations manager:

- starts on Executive Overview
- checks on-time delivery rate and monthly delay trend
- drills into Supplier Analytics or Warehouse Operations when performance drops

Logistics analyst:

- reviews top delay reasons
- investigates supplier and warehouse drivers
- exports high-risk shipment lists for follow-up

Warehouse manager:

- monitors overload flag rate
- reviews inventory stockout risk
- prioritizes warehouse/process issues

Business analyst:

- uses the dashboard to explain what changed, where it changed, and what action should be taken

## Screenshot Placeholder Structure

```text
dashboards/screenshots/
|-- executive_overview.png
|-- supplier_analytics.png
|-- warehouse_operations.png
`-- shipment_risk_monitoring.png
```

## Git Commit Suggestions

```text
docs: add Power BI dashboard planning guide
feat: add Power BI optimized SQL queries
docs: add dashboard page wireframes and KPI definitions
docs: add screenshot placeholder structure
docs: document Power BI stakeholder workflow
```

