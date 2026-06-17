# Audit Log Screen Spec

## Purpose
The Audit Log screen provides a traceable history of key system and user actions for compliance, debugging, and review.

## Goals
- Record key operational events
- Support traceability for AML review workflows
- Allow filtering and inspection of activity history
- Make the system easier to audit during demos and reports

## Layout
### Top filter bar
- Search input
- Action type filter
- Actor role filter
- Date range filter

### Main content
- Activity timeline or table
- Optional event detail drawer

## Core components
### Filters
- Action type selector
- Actor selector
- Date range picker
- Keyword search

### Audit records table / timeline
- Timestamp
- Actor
- Action type
- Target entity
- Short description
- Status or result

### Detail view
- Event metadata
- Related transaction or alert id
- Payload summary
- Outcome

## Event categories
- Prediction event
- Manual flag event
- Escalate / dismiss event
- Rule create / update / delete
- Rule reload
- API test execution
- Batch job completion

## Interaction model
- Clicking an event opens detail drawer
- Filters update instantly without changing the page structure
- Export action should be available if needed

## States
### Loading
- Skeleton rows

### Empty
- Show an empty state if no audit records exist or match the filter set

### Error
- Show retryable error if audit retrieval fails

## Notes
This page strengthens traceability and supports the AML domain expectation of clear operational history.
