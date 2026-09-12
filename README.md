# Process and Maintenance Engineering System

A company-wide Streamlit system for process engineering, maintenance engineering, engineering trials, machinery/tooling research, asset management and engineering knowledge.

Live app: https://process-and-maintenance-engineering-system-web.streamlit.app

## Core design

The system uses hidden UUIDs for internal relationships. Human-facing business IDs, legacy IDs and aliases are optional and can be added later without breaking links between records.

Persistence is local-first: records are held in the current Streamlit session and can be downloaded as JSON or as a full ZIP backup. No persistent cloud database is configured.

## Current modules

- Dashboard with engineering workload, PM due/overdue, breakdown downtime, MTTR and MTBF
- Asset Register with full equipment profiles, criticality, utilities, safety, configuration and maintenance history
- Products & Process Routes linking materials, departments, operations, assets, setup references and inspection requirements
- Engineering Action Register
- Preventive Maintenance Schedules with task checklists, due dates, safety requirements and parts requirements
- Maintenance & Breakdown Management linked to assets, PM schedules, engineering actions and RCA records
- Process Engineering & Improvement with cycle-time, rejection, tool-life and annual benefit tracking
- Engineering Trials / Experimental Records
- Machinery & Tooling Research / Recommendation records
- Tooling Knowledge Library
- Spare Parts / Consumables Register
- Root Cause Analysis & Engineering Investigations
- Engineering Management PDF reporting
- System JSON and ZIP backup

## Engineering Operations

The dedicated **Engineering Operations** page provides the day-to-day execution layer.

### Preventive maintenance execution

- Complete PM work directly from its schedule
- Task-by-task checklist tick-off before closure
- Automatic next-due calculation for daily, weekly, monthly, quarterly, six-monthly, annual and custom intervals
- Create a linked maintenance-history record automatically
- Record technician, actual labour hours, labour rate and external/service cost
- Select stocked parts consumed during the PM
- Automatically deduct consumed quantities from spare-parts stock
- Calculate labour, parts, external and total maintenance cost

### Machine-specific maintenance packs

Initial engineering maintenance packs are included for:

- CNC
- Grinding
- Cutting
- Laser
- Filtration
- Chiller
- Extraction
- Pump
- Vacuum
- Furnace

These packs are starting templates only. They must be verified against the actual machine, OEM documentation and internal engineering requirements before they become controlled maintenance standards. Laser tasks are intentionally high-level because in-house laser design/configuration must determine the final maintenance requirements.

Templates can be added to the PM library and then applied to individual assets to create live schedules.

### Breakdown and reliability workflow

- Create a linked Engineering Action directly from a breakdown
- Create a linked RCA directly from a breakdown
- Add a failure-category tag to breakdown records
- Detect recurring failure groups
- Downtime Pareto by asset
- Breakdown count and cumulative downtime analysis
- Combined linked Asset Engineering History across maintenance, PM, actions, process improvements, trials, RCA, routes, tooling and spares

### Spare-parts control

- Low-stock and out-of-stock warnings
- Quantity-on-hand updates
- Minimum-stock levels
- Unit cost
- Storage location
- Automatic stock deduction from PM execution

### Maintenance cost control

- Labour cost = actual maintenance hours × labour rate
- Parts cost from stocked components consumed
- External/service costs
- Total maintenance cost per maintenance record
- Maintenance-cost analysis by asset
- Cost ledger across maintenance history

The first operational helpers are in `next_layer.py`. Advanced execution, stock-consumption, reliability analytics and standard maintenance packs are implemented in `advanced_operations.py`. The Streamlit operations page is `pages/1_Engineering_Operations.py`.

## Materials and departments

Default materials include Glass, Silon, Alumina and Quartz. Materials, departments and asset classes can be changed from System Data & Backup.

## JSON compatibility

Schema: `process-maintenance-engineering-system`

The core file remains compatible with version 1 and version 2 JSON backups. New operational fields are additive. The PM template collection is added dynamically and is preserved in downloaded system JSON because unknown top-level collections are retained by the loader.

## Privacy / storage

The hosted Streamlit app does not use a persistent database. Uploaded JSON is processed by the hosted Streamlit session, so data does travel to the Streamlit server during use. Downloaded JSON/ZIP files are the intended persistent record. If data must never leave the local computer, run the app locally instead of using the hosted deployment.
