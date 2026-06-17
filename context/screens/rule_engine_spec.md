# Rule Engine Screen Spec

## Purpose
The Rule Engine screen provides CRUD management for AML rules, including validation, enable/disable behavior, version awareness, and reload actions.

## Goals
- Manage rules as first-class operational assets
- Support rule creation, editing, deletion, and activation
- Show rule metadata and version history
- Provide safe reload flows for the active rule set

## Layout
### Top action row
- Search bar
- Filter controls
- Create Rule button
- Reload Rules button

### Main area
- Rules table
- Optional detail drawer or modal for the selected rule

## Core components
### Filters and search
- Search by rule id or typology
- Severity filter
- Enabled / disabled filter
- Typology filter
- Version filter

### Rules table
- Rule id
- Typology
- Severity
- Condition summary
- Enabled state
- Updated at
- Action column

### Form / editor
- Rule id input
- Typology select
- Severity select
- Condition editor / DSL textarea
- Action hint field
- Enabled switch
- Save / cancel buttons

### Supporting panels
- Validation helper text
- Version history panel
- Reload status banner
- Rule test preview panel

## Interaction model
- Create and edit should keep field-level validation visible
- Enable / disable can be a fast toggle
- Delete must require confirmation
- Reload should be explicit and traceable

## States
### Loading
- Skeleton table rows

### Empty
- Empty state with a prompt to create the first rule

### Error
- Inline validation errors for invalid syntax or unknown fields
- Banner for reload failures or save conflicts

## Notes
When possible, use a drawer for edit flows to preserve list context. Use a full-page form only if the rule editor grows too large for comfortable editing.
