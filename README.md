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

## Engineering Operations next layer

A dedicated **Engineering Operations** page adds the day-to-day workflow layer:

- Complete a PM directly from its schedule
- Automatically calculate the next due date for daily, weekly, monthly, quarterly, six-monthly, annual and custom interval PMs
- Record PM completion as a linked maintenance-history event
- Create reusable machine / asset-class PM templates
- Apply a PM template to an asset to create a live schedule
- Create a linked Engineering Action directly from a breakdown
- Create a linked RCA directly from a breakdown
- Review a combined Asset Engineering History timeline across maintenance, PM, actions, process improvements, trials, RCA, routes, tooling and spares
- Low-stock and out-of-stock spare warnings
- Update stock quantities and minimum-stock levels
- Edit the identity and legacy/business IDs of existing records without changing their hidden system UUID

The operational helpers are implemented in `next_layer.py` and the Streamlit page is `pages/1_Engineering_Operations.py`.

## Materials and departments

Default materials include Glass, Silon, Alumina and Quartz. Materials, departments and asset classes can be changed from System Data & Backup.

## JSON compatibility

Schema: `process-maintenance-engineering-system`

The core file remains compatible with version 1 and version 2 JSON backups. The new PM template collection is added dynamically by the Engineering Operations page and is preserved in downloaded system JSON because unknown top-level collections are retained by the loader.

## Privacy / storage

The hosted Streamlit app does not use a persistent database. Uploaded JSON is processed by the hosted Streamlit session, so data does travel to the Streamlit server during use. Downloaded JSON/ZIP files are the intended persistent record. If data must never leave the local computer, run the app locally instead of using the hosted deployment.