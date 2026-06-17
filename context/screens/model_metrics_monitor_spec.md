# Model & Metrics Monitor Screen Spec

## Purpose
The Model & Metrics Monitor screen provides a focused observability view for Prometheus metrics, system health, latency, throughput, drift, and explanation quality.

## Goals
- Monitor technical health in a single place
- Visualize Prometheus metrics clearly
- Surface model and rule performance indicators
- Show explanation success and fallback behavior

## Layout
### Top summary row
- Health KPIs
- Short status indicators

### Chart grid
- Latency chart
- Throughput chart
- Request rate chart
- Decision distribution chart
- Rule hit trend chart

### Lower section
- Drift cards
- Explanation quality cards
- Metrics details table or timeline

## Core components
### Health cards
- API health
- Model loaded
- Rule engine loaded
- Database connectivity
- Redis connectivity

### Charts
- p95 latency
- request volume over time
- alert rate over time
- decision distribution
- rule trigger counts

### Drift / quality widgets
- Drift indicator card
- Explanation success rate
- Explanation fallback rate
- LLM latency card

## Interaction model
- Refresh metrics manually
- Change time window
- Drill into individual chart details if needed

## States
### Loading
- Show skeleton cards and chart placeholders

### Empty
- Show a message when no metric window is available yet

### Error
- Show a retry action if scrape or data retrieval fails

## Notes
This page can remain lean and technical. If a metric is only needed as a summary, it may also appear in the Dashboard.
