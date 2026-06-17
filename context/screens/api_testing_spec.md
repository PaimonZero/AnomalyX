# API Testing (Demo) Screen Spec

## Purpose
The API Testing screen provides a Postman-like interface for testing AnomalyX endpoints individually.

## Goals
- Let users construct requests interactively
- Support quick testing of all public and protected endpoints
- Display response data clearly
- Preserve request history for replay and demo

## Layout
### Left side
- Endpoint picker
- Method selector
- Auth / token input
- Request builder sections

### Right side
- Response viewer
- Status and latency summary
- Optional headers / raw view toggle

### Bottom section
- Request history
- Saved sample presets

## Core components
### Request builder
- Method dropdown
- Endpoint dropdown
- Headers editor
- Query params editor
- JSON body editor
- Example payload presets
- Send button
- Save request button

### Response viewer
- HTTP status badge
- Latency badge
- Pretty JSON response viewer
- Raw response toggle
- Copy response button
- Response headers viewer

### History / presets
- Recent request list
- Saved samples list
- Replay action

## Supported endpoints
- `/health`
- `/metrics`
- `/api/v1/predict`
- `/api/v1/batch-score`
- `/api/v1/alerts`
- `/api/v1/alerts/{id}`
- `/api/v1/alerts/{id}/status`
- `/api/v1/rules`
- `/api/v1/rules/reload`

## Interaction model
- Selecting an endpoint may preload an example request body
- Send action should update the response panel without changing the overall layout height
- History items should be reusable as demo presets

## States
### Loading
- Show request and response skeletons when an example payload or response is being fetched

### Empty
- Show a starter example request for `/api/v1/predict`

### Error
- Show HTTP errors clearly in the response panel with the returned payload

## Notes
This screen should feel like a compact, polished demo tool rather than a full IDE.
