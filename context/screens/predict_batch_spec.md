# Predict Batch Screen Spec

## Purpose
The Predict Batch screen allows users to upload or paste transaction data, validate the input, and run batch anomaly scoring.

## Goals
- Support bulk scoring workflows
- Provide clear validation before execution
- Show progress and result summaries
- Allow row-level inspection of flagged cases

## Layout
### Left panel
- File upload zone
- Paste JSON input tab
- Batch configuration form
- Validation summary
- Run button area

### Right panel
- Preview and validation results
- Batch progress indicator
- Summary cards
- Batch results table

## Core components
### Input components
- Drag-and-drop file uploader
- CSV / JSON format selector
- JSON textarea input
- Batch name input
- Optional threshold override input
- Optional output format selector

### Validation components
- Schema validation panel
- Row error list
- Missing field highlights
- Preview row count

### Execution components
- Run Batch button
- Reset button
- Cancel button if job is still running
- Progress bar

### Result components
- Total rows card
- Processed rows card
- Flagged rows card
- Failed rows card
- Average risk score card
- Results table

## Interaction model
- Validate before running
- Prevent execution if required schema checks fail
- Clicking a row opens the Batch Record Detail Modal
- Export should be available after completion

## States
### Loading
- Show upload and result skeletons while processing state is unknown

### Empty
- Show a dropzone-based empty state encouraging file upload or paste input

### Error
- Show validation errors in-line for malformed rows
- Show execution errors as a non-blocking banner with retry guidance

## Notes
If batch processing becomes asynchronous, the UI should treat it as a job with status polling instead of a one-shot request.
