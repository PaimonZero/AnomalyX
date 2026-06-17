# Settings Screen Spec

## Purpose
The Settings screen exposes environment and demo-related configuration for the AnomalyX Admin Console.

## Goals
- Make demo control simple
- Show environment and integration status
- Provide a small set of operational configuration options
- Avoid turning the page into a complex admin panel

## Layout
### Sectioned settings cards
- Environment status
- Auth / token demo config
- Feature flags
- Threshold defaults
- Provider / repository status

### Footer actions
- Save
- Reset to default
- Copy demo token

## Core components
### Environment card
- Current environment label
- Backend mode status
- Repository status
- Monitoring status

### Configuration form
- Demo token input or read-only display
- Threshold defaults
- Feature flag toggles
- Optional provider selector display

### Action buttons
- Save settings
- Reset defaults
- Copy value button

## Interaction model
- Save should validate inputs before writing
- Reset should require confirmation if it changes demo behavior
- Copy token should give immediate feedback via toast

## States
### Loading
- Skeleton settings cards

### Empty
- Show defaults if no config has been explicitly set

### Error
- Show inline validation messages and a retryable save failure banner

## Notes
Keep this page intentionally small. It is mainly for demo readiness and environment visibility, not for complex configuration.
