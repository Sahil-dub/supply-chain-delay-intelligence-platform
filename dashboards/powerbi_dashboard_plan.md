# Power BI Dashboard Plan

## Dashboard Goal

The Power BI dashboard should help operations and logistics stakeholders monitor delivery performance, identify bottlenecks, and prioritize follow-up actions.

The dashboard is designed for:

- Operations managers
- Logistics analysts
- Warehouse managers
- Business analysts
- Supply chain analysts

## Pages

1. Executive Overview
2. Supplier Analytics
3. Warehouse Operations
4. Shipment Risk Monitoring

## Theme Recommendation

Use a calm operational theme:

- Background: `#F7F9FC`
- Primary text: `#1F2937`
- Secondary text: `#6B7280`
- Primary blue: `#2563EB`
- Success green: `#16A34A`
- Warning amber: `#F59E0B`
- Risk red: `#DC2626`
- Neutral grid line: `#E5E7EB`

Use red only for genuine exceptions such as high delay rate, critical risk, or stockout risk. This keeps the dashboard professional and avoids alarm fatigue.

## Global Slicers

Recommended slicers across pages:

- Delivery month
- Supplier reliability band
- Warehouse city
- Product category
- Shipment priority
- Delay reason

## Page 1: Executive Overview

### Purpose

Give leadership a fast view of delivery health and whether delays are improving or worsening.

### KPI Cards

- Total shipments
- Delayed shipments
- On-time delivery rate
- Average delay days

### Recommended Visuals

- KPI cards across the top.
- Line chart: monthly delay rate trend.
- Clustered column chart: delivered vs delayed shipments by month.
- Bar chart: top delay reasons.
- Small table: highest-risk shipments.

### Wireframe

```text
+--------------------------------------------------------------+
| Executive Overview                                           |
| [Month] [Warehouse] [Category] [Supplier Band]                |
+------------+------------+------------+-----------------------+
| Shipments  | Delayed    | On-Time %  | Avg Delay Days        |
+------------+------------+------------+-----------------------+
| Delay Rate Trend Over Time                                   |
| [Line chart]                                                 |
+-----------------------------+--------------------------------+
| Top Delay Reasons           | High-Risk Shipment Preview      |
| [Bar chart]                 | [Table]                        |
+-----------------------------+--------------------------------+
```

## Page 2: Supplier Analytics

### Purpose

Help analysts understand which suppliers contribute most to late shipments and which suppliers are stable.

### Recommended Visuals

- Table: supplier reliability ranking.
- Bar chart: delayed shipments by supplier.
- Scatter plot: reliability score vs on-time delivery rate.
- Donut or stacked bar: supplier risk segmentation.

### Wireframe

```text
+--------------------------------------------------------------+
| Supplier Analytics                                           |
| [Month] [Supplier Country] [Reliability Band] [Category]      |
+-----------------------------+--------------------------------+
| Supplier Reliability Ranking | Supplier Risk Segmentation     |
| [Table]                     | [Stacked bar]                  |
+-----------------------------+--------------------------------+
| Delay Contribution by Supplier                               |
| [Horizontal bar chart]                                       |
+--------------------------------------------------------------+
| Reliability Score vs On-Time Delivery Rate                   |
| [Scatter plot]                                               |
+--------------------------------------------------------------+
```

## Page 3: Warehouse Operations

### Purpose

Help warehouse and logistics teams identify fulfillment bottlenecks and inventory pressure.

### Recommended Visuals

- Bar chart: warehouse delay rate.
- Bar chart: overload flag rate by warehouse.
- Matrix: stockout risk by warehouse and category.
- Table: high-risk inventory positions.

### Wireframe

```text
+--------------------------------------------------------------+
| Warehouse Operations                                         |
| [Month] [Warehouse City] [Category] [Stockout Risk Level]     |
+-----------------------------+--------------------------------+
| Warehouse Delay Rate        | Overload Flag Rate              |
| [Bar chart]                 | [Bar chart]                    |
+-----------------------------+--------------------------------+
| Inventory Stockout Risk Matrix                               |
| [Matrix: warehouse x category]                               |
+--------------------------------------------------------------+
| High-Risk Inventory Positions                                |
| [Table]                                                      |
+--------------------------------------------------------------+
```

## Page 4: Shipment Risk Monitoring

### Purpose

Give operations users an exception-monitoring view for shipments needing action.

### Recommended Visuals

- KPI cards: critical shipments, high-risk shipments, average delay days.
- Table: high-risk shipments.
- Bar chart: delay reasons.
- Stacked bar: risk level by priority.

### Wireframe

```text
+--------------------------------------------------------------+
| Shipment Risk Monitoring                                     |
| [Month] [Priority] [Delay Reason] [Risk Level]                |
+------------+------------+------------+-----------------------+
| Critical   | High Risk  | Avg Delay  | Delayed Value         |
+------------+------------+------------+-----------------------+
| High-Risk Shipments Table                                    |
| [Table with conditional formatting]                          |
+-----------------------------+--------------------------------+
| Delay Reasons               | Risk Level by Priority          |
| [Bar chart]                 | [Stacked bar]                  |
+-----------------------------+--------------------------------+
```

## Screenshot Placeholder Structure

Save dashboard screenshots here after building the Power BI report:

```text
dashboards/screenshots/
|-- executive_overview.png
|-- supplier_analytics.png
|-- warehouse_operations.png
`-- shipment_risk_monitoring.png
```

## Interaction Ideas

- Clicking a supplier filters shipment risk and delay reason visuals.
- Selecting a warehouse filters inventory risk and shipment bottleneck visuals.
- Selecting a month filters all pages to compare seasonal peaks.
- Drill-through from supplier or warehouse pages to shipment risk monitoring.
- Conditional formatting highlights critical shipments and high stockout risk.

## Power BI Workflow

1. Load PostgreSQL views or query outputs from `sql/powerbi_dashboard_queries.sql`.
2. Set correct data types for dates, percentages, and currency fields.
3. Create relationships only when importing separate dimension/fact tables.
4. Create DAX measures for KPI cards if using imported tables.
5. Build the four report pages from the wireframes.
6. Add slicers and cross-filter interactions.
7. Export screenshots into `dashboards/screenshots/`.
8. Add screenshots to the README during final documentation polish.

