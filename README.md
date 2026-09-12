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

## Materials and departments

Default materials include Glass, Silon, Alumina and Quartz. Materials, departments and asset classes can be changed from System Data & Backup.

## JSON compatibility

Schema: `process-maintenance-engineering-system`

Current schema version: `2`

Version 1 system JSON files remain loadable. New v2 collections are added automatically when older files are loaded.

## Privacy / storage

The hosted Streamlit app does not use a persistent database. Uploaded JSON is processed by the hosted Streamlit session, so data does travel to the Streamlit server during use. Downloaded JSON/ZIP files are the intended persistent record. If data must never leave the local computer, run the app locally instead of using the hosted deployment.
