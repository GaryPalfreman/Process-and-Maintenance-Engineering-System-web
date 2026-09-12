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

The **Engineering Operations** page provides the day-to-day execution layer:

- Task-by-task PM completion
- Automatic next-due calculation
- Technician, labour, service and parts cost capture
- Automatic spare stock deduction
- Machine-specific maintenance packs
- Breakdown follow-up to Engineering Action or RCA
- Failure categorisation and recurring-failure detection
- Downtime Pareto
- Maintenance cost analysis
- Linked Asset Engineering History

Initial engineering maintenance packs are included for CNC, Grinding, Cutting, Laser, Filtration, Chiller, Extraction, Pump, Vacuum and Furnace. These are starting templates and must be verified against the actual machine, OEM documentation and internal engineering requirements before adoption as controlled maintenance standards. Laser tasks are intentionally high-level because in-house laser design/configuration must determine the final maintenance requirements.

Operational helpers are in `next_layer.py` and `advanced_operations.py`. The operations page is `pages/1_Engineering_Operations.py`.

## Engineering Control Centre

The new **Engineering Control Centre** moves the application toward a lightweight combined CMMS + Process Engineering + Engineering Knowledge System.

### Maintenance work orders

- Create planned, corrective, breakdown follow-up, inspection, improvement and project work orders
- Link work orders to assets, maintenance records and engineering actions
- Track priority, owner, due date, scope, planned labour and planned downtime
- Record actual labour, actual downtime, progress and completion notes

### Planned shutdown management

- Create shutdown/outage plans
- Define affected assets, coordinator, dates and scope
- Capture pre-work, parts readiness, contractor requirements, isolation/permit planning and restart validation
- Link maintenance work orders into each shutdown

### Condition monitoring

- Record asset condition readings such as vibration, concentration, temperature, pressure or internally defined process health metrics
- Define warning and critical limits with high- or low-direction alarms
- Show current Normal / Warning / Critical condition status
- Plot reading trends by asset and metric

### Asset criticality and risk scoring

Asset risk uses a simple configurable engineering score:

`(Safety + Production + Quality + Repair/Lead-Time consequence) × Likelihood`

Each factor is rated 1–5, producing a score from 4–100 and a Low / Moderate / High / Critical risk band. The resulting band updates the asset criticality field without changing its hidden UUID.

### Automatic RCA recommendations

Breakdowns can be recommended for RCA when one or more triggers are met:

- Downtime exceeds the selected threshold
- Maintenance cost exceeds the selected threshold
- The asset is High or Critical risk
- A recurring failure pattern is detected
- The breakdown is marked as having safety or quality impact

The recommendation remains advisory; the engineer chooses whether to create the RCA.

### Engineering handover dashboard

The handover dashboard consolidates:

- Assets down / under repair
- Open work orders
- High and Critical engineering actions
- PM due within the selected horizon
- Condition-monitoring warnings and critical alarms
- Upcoming planned shutdowns
- Actions awaiting parts or supplier response
- Open engineering handover notes

The control-centre logic is implemented in `control_centre.py`. The Streamlit page is `pages/2_Engineering_Control_Centre.py`.

## Materials and departments

Default materials include Glass, Silon, Alumina and Quartz. Materials, departments and asset classes can be changed from System Data & Backup.

## JSON compatibility

Schema: `process-maintenance-engineering-system`

The core loader remains compatible with version 1 and version 2 JSON backups. New operational and control-centre collections are additive and are preserved in downloaded system JSON because unknown top-level collections are retained by the loader.

## Privacy / storage

The hosted Streamlit app does not use a persistent database. Uploaded JSON is processed by the hosted Streamlit session, so data does travel to the Streamlit server during use. Downloaded JSON/ZIP files are the intended persistent record. If data must never leave the local computer, run the app locally instead of using the hosted deployment.
