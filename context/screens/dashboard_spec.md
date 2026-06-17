# Dashboard Screen Spec

## Purpose
The Dashboard is the main landing page of the AnomalyX Admin Console. It provides a system-wide operational overview for Admin, Compliance Officer, and ML/Risk Engineer users.

## Goals
- Summarize current system health
- Show high-level observability metrics from Prometheus
- Surface the latest alerts, batch jobs, and API tests
- Provide quick navigation into the main workflows

## Layout
### App shell
- Fixed sidebar on the left
- Top header bar with page title, environment badge, search, and user menu
- Main content area using a responsive grid

### Main page structure
1. KPI summary row
2. Prometheus metrics preview row
3. Service health and system status row
4. Recent operational activity section
5. Quick actions panel

## Core components
### KPI cards
- Total predictions
- Flagged alerts
- High / Critical alerts
- Average latency
- Explanation success rate
- Rule hit rate

### Monitoring widgets
- Requests over time chart
- p95 latency chart
- Decision distribution chart
- Rule trigger trend chart
- Mini Prometheus chart cards

### Health cards
- API health
- Model loaded
- Rule engine loaded
- Postgres connectivity
- Redis connectivity

### Activity tables / lists
- Recent alerts
- Recent batch jobs
- Recent API tests

### Quick actions
- Open Alerts / Review Queue
- Run Predict Batch
- Open API Testing
- Open Rule Engine
- Open Monitoring

## Interaction model
- Clicking an alert row opens the Alert Detail Modal
- Clicking a batch row opens the Batch Record Detail Modal
- Clicking a chart card can filter the related table or navigate to the full Monitoring page
- Quick actions act as primary shortcuts for demo flow

## States
### Loading
- Show skeleton cards and chart placeholders

### Empty
- Show a welcoming empty state with a single CTA to start a batch or open API testing

### Error
- Show a compact error banner if metrics or activity data cannot load
- Keep the rest of the dashboard visible if partial data is available

## Content prioritization
If a widget is not large enough to justify a full page, it should live here as a compact summary rather than becoming a separate screen.

## Notes
The Dashboard should feel compact, informative, and demo-friendly. It is the default home for the product.
