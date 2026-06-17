# Alerts / Review Queue Screen Spec

## Purpose
The Alerts / Review Queue is the primary review workspace for suspicious transactions. It enables Compliance Officers and Admin users to inspect alerts, filter the queue, and take review actions.

## Goals
- List all flagged or reviewable alerts in one place
- Support fast filtering and prioritization
- Allow inspection of evidence and explanation
- Allow manual flagging, escalation, and dismissal

## Layout
### Header area
- Page title
- Search input
- Filter controls
- Bulk action controls

### Main content
- Alerts data table
- Optional right-side detail drawer or modal preview
- Pagination or infinite scroll footer

## Core components
### Filter bar
- Search by alert id / transaction id
- Status filter
- Risk level filter
- Date range picker
- Source filter
- Sort control

### Alerts table
- Alert id
- Transaction id
- Risk score
- Risk level
- Status
- Triggered rules
- Updated at
- Action column

### Bulk actions
- Bulk escalate
- Bulk dismiss
- Bulk mark reviewed

## Interaction model
- Clicking a row opens the Alert Detail Modal
- Bulk selection enables multi-record actions
- Filters should update the table without losing the current context

## States
### Loading
- Skeleton rows in the table

### Empty
- Inform the user that no alerts match the current filters

### Error
- Show a retryable fetch error if the queue cannot be loaded

## Notes
This page should be the default operational entry point for compliance review. It is intentionally separate from the Dashboard because alert review is a distinct recurring workflow.
