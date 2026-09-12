# Process and Maintenance Engineering System

A local-first Streamlit engineering management system for company-wide process engineering and maintenance work.

## Current modules

- Dashboard
- Engineering Actions
- Process Engineering / Improvements
- Maintenance & Breakdowns
- Asset Register
- Engineering Trials
- Machinery & Tooling Research
- RCA & Investigations
- System Data & Backup

## Design principles

- Hidden UUIDs are used for record relationships.
- Human-facing IDs are optional and editable later.
- Business IDs, legacy IDs and aliases can be added without breaking linked records.
- Data is persisted by downloading a complete system JSON file locally.
- The hosted app does not deliberately keep a permanent online engineering database.
- A local backup ZIP and management summary PDF can be generated.

## Initial material coverage

The default material list includes:

- Glass
- Silon
- Alumina
- Quartz

The list is configurable from the System Data & Backup page.

## Asset coverage

The asset register is intended to cover CNC equipment, grinding and cutting machines, laser systems, filtration, chillers, extraction, measuring equipment, internally developed/custom equipment and other maintainable assets.

## Deployment

- Repository: `GaryPalfreman/Process-and-Maintenance-Engineering-System-web`
- Branch: `main`
- Main file: `app.py`

## Privacy note

When this application is hosted on Streamlit Community Cloud, any JSON file uploaded to restore a system session is transmitted to the hosted Streamlit process for temporary processing. If records must never leave the local computer, run the application locally instead.
