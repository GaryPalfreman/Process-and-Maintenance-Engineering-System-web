from datetime import date

import pandas as pd
import streamlit as st

from engineering_system import (
    asset_label_by_uuid,
    backup_zip,
    base_record,
    blank_store,
    dashboard_metrics,
    generate_summary_pdf,
    load_store,
    record_label,
    records_dataframe,
    store_bytes,
)

st.set_page_config(page_title="Process and Maintenance Engineering System", page_icon="🛠️", layout="wide")

st.markdown(
    """
    <style>
    .block-container {max-width: 1450px; padding-top: 1.2rem; padding-bottom: 3rem;}
    div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.22); border-radius:14px; padding:12px 14px;}
    .pm-card {border:1px solid rgba(128,128,128,.23); border-radius:14px; padding:14px 16px; margin:.4rem 0 .8rem 0;}
    .muted {opacity:.72;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "pm_store" not in st.session_state:
    st.session_state.pm_store = blank_store()

store = st.session_state.pm_store


def add_record(module, record):
    record["updated_at"] = record.get("created_at")
    store[module].append(record)


def delete_record(module, system_uuid):
    store[module] = [r for r in store[module] if r.get("system_uuid") != system_uuid]


def department_options():
    current = [str(x).strip() for x in store.get("settings", {}).get("departments", []) if str(x).strip()]
    return current


def asset_options():
    return {record_label(a): a.get("system_uuid") for a in store.get("assets", [])}


with st.sidebar:
    st.header("Engineering System")
    page = st.radio(
        "Module",
        [
            "Dashboard",
            "Engineering Actions",
            "Process Engineering",
            "Maintenance",
            "Assets",
            "Engineering Trials",
            "Machinery & Tooling Research",
            "RCA & Investigations",
            "System Data & Backup",
        ],
    )
    st.divider()
    upload = st.file_uploader("Load system JSON", type=["json"], key="load_pm_system")
    if upload is not None:
        try:
            loaded = load_store(upload.getvalue())
        except Exception as exc:
            st.error(f"Could not load this system file: {exc}")
        else:
            load_key = f"{upload.name}:{len(upload.getvalue())}"
            if st.session_state.get("pm_loaded_key") != load_key:
                st.session_state.pm_store = loaded
                st.session_state.pm_loaded_key = load_key
                st.rerun()

st.title("Process and Maintenance Engineering System")
st.caption("Company-wide process engineering, maintenance, asset, trial, research and investigation management. Human-facing IDs remain optional and editable; system relationships use hidden UUIDs.")

if page == "Dashboard":
    metrics = dashboard_metrics(store)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Assets", metrics["assets"])
    c2.metric("Open actions", metrics["open_actions"])
    c3.metric("Critical actions", metrics["critical_actions"])
    c4.metric("Breakdowns", metrics["breakdowns"])
    c5.metric("Downtime (h)", f"{metrics['downtime_hours']:.1f}")
    c6.metric("PM due / overdue", metrics["due_pm"])

    st.markdown("### Engineering workload")
    actions = pd.DataFrame(store.get("actions", []))
    if actions.empty:
        st.info("No engineering actions recorded yet.")
    else:
        cols = [c for c in ["priority", "status", "department", "title", "owner", "due_date"] if c in actions.columns]
        st.dataframe(actions[cols], use_container_width=True, hide_index=True)

    st.markdown("### Recent maintenance / breakdown activity")
    maint = store.get("maintenance", [])
    if not maint:
        st.info("No maintenance records yet.")
    else:
        rows = []
        for r in maint[-12:][::-1]:
            rows.append({
                "Date": r.get("event_date", ""),
                "Type": r.get("maintenance_type", ""),
                "Department": r.get("department", ""),
                "Asset": asset_label_by_uuid(store, r.get("asset_uuid", "")),
                "Status": r.get("status", ""),
                "Downtime h": r.get("downtime_hours", 0),
                "Summary": r.get("title", ""),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

elif page == "Assets":
    st.subheader("Asset Register")
    st.caption("Use this for CNC, grinders, glass cutting equipment, laser systems, chillers, extraction, filtration, pumps, measuring equipment, custom-built machinery and other maintainable assets.")

    with st.form("asset_form", clear_on_submit=True):
        a1, a2, a3 = st.columns(3)
        title = a1.text_input("Asset / equipment name")
        department = a2.text_input("Department")
        asset_class = a3.selectbox("Asset class", ["CNC", "Grinding", "Cutting", "Laser", "Filtration", "Chiller", "Extraction", "Measuring", "Custom Equipment", "Other"])
        b1, b2, b3 = st.columns(3)
        manufacturer = b1.text_input("Manufacturer")
        model = b2.text_input("Model")
        serial = b3.text_input("Serial number")
        c1, c2, c3 = st.columns(3)
        business_id = c1.text_input("Current / business ID (optional)")
        legacy_id = c2.text_input("Legacy ID (optional)")
        alias = c3.text_input("Alias / alternate ID (optional)")
        d1, d2, d3 = st.columns(3)
        location = d1.text_input("Location")
        criticality = d2.selectbox("Criticality", ["Low", "Medium", "High", "Critical"])
        status = d3.selectbox("Asset status", ["Active", "Standby", "Under Repair", "Decommissioned"])
        notes = st.text_area("Function / configuration / notes")
        submitted = st.form_submit_button("Add Asset", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Asset / equipment name is required.")
        else:
            r = base_record("asset", title, department, business_id, legacy_id)
            r.update({"alias": alias, "asset_class": asset_class, "manufacturer": manufacturer, "model": model, "serial_number": serial, "location": location, "criticality": criticality, "status": status, "notes": notes})
            add_record("assets", r)
            st.rerun()

    for i, r in enumerate(store["assets"]):
        st.markdown(f"<div class='pm-card'><b>{record_label(r)}</b><br><span class='muted'>{r.get('department','')} · {r.get('asset_class','')} · {r.get('manufacturer','')} {r.get('model','')} · {r.get('status','')}</span><br>{r.get('notes','')}</div>", unsafe_allow_html=True)
        if st.button("Remove asset", key=f"del_asset_{i}"):
            delete_record("assets", r["system_uuid"])
            st.rerun()

elif page == "Engineering Actions":
    st.subheader("Engineering Action Register")
    with st.form("action_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Action / issue")
        department = c2.text_input("Department")
        category = c3.selectbox("Category", ["Process", "Maintenance", "Quality", "R&D", "Capital Equipment", "Tooling", "Safety", "Other"])
        d1, d2, d3, d4 = st.columns(4)
        priority = d1.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        status = d2.selectbox("Status", ["Open", "Investigation", "Trial", "Awaiting Parts", "Awaiting Supplier", "Validation", "Complete", "Closed"])
        owner = d3.text_input("Owner")
        due_date = d4.date_input("Due date", value=date.today())
        business_id = st.text_input("Current / legacy action ID (optional)")
        detail = st.text_area("Problem / required action / notes")
        submitted = st.form_submit_button("Add Engineering Action", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Action title is required.")
        else:
            r = base_record("engineering_action", title, department, business_id, "")
            r.update({"category": category, "priority": priority, "status": status, "owner": owner, "due_date": due_date.isoformat(), "detail": detail})
            add_record("actions", r)
            st.rerun()

    if store["actions"]:
        df = records_dataframe(store["actions"])
        show = [c for c in ["business_id", "priority", "status", "department", "category", "title", "owner", "due_date"] if c in df.columns]
        st.dataframe(df[show], use_container_width=True, hide_index=True)

elif page == "Maintenance":
    st.subheader("Maintenance & Breakdown Management")
    st.caption("Covers preventive, predictive, corrective and breakdown maintenance across all departments and asset classes.")
    amap = asset_options()
    with st.form("maintenance_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Maintenance / fault summary")
        department = c2.text_input("Department")
        maintenance_type = c3.selectbox("Maintenance type", ["Preventive", "Predictive", "Corrective", "Breakdown", "Improvement"])
        d1, d2, d3 = st.columns(3)
        selected_asset = d1.selectbox("Asset", [""] + list(amap.keys()))
        event_date = d2.date_input("Date", value=date.today())
        status = d3.selectbox("Status", ["Planned", "Due", "Overdue", "In Progress", "Complete", "Monitoring"])
        e1, e2, e3 = st.columns(3)
        downtime = e1.number_input("Downtime hours", min_value=0.0, step=0.25)
        owner = e2.text_input("Engineer / technician")
        business_id = e3.text_input("Work order / legacy ID (optional)")
        symptom = st.text_area("Symptoms / requirement")
        diagnosis = st.text_area("Diagnosis / findings")
        action_taken = st.text_area("Repair / maintenance completed")
        parts = st.text_area("Parts / consumables used")
        submitted = st.form_submit_button("Add Maintenance Record", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Maintenance summary is required.")
        else:
            r = base_record("maintenance", title, department, business_id, "")
            r.update({"maintenance_type": maintenance_type, "asset_uuid": amap.get(selected_asset, ""), "event_date": event_date.isoformat(), "status": status, "downtime_hours": float(downtime), "owner": owner, "symptom": symptom, "diagnosis": diagnosis, "action_taken": action_taken, "parts_used": parts})
            add_record("maintenance", r)
            st.rerun()

    if store["maintenance"]:
        rows = []
        for r in store["maintenance"]:
            rows.append({"Date": r.get("event_date"), "Type": r.get("maintenance_type"), "Status": r.get("status"), "Department": r.get("department"), "Asset": asset_label_by_uuid(store, r.get("asset_uuid", "")), "Downtime h": r.get("downtime_hours", 0), "Summary": r.get("title")})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

elif page == "Process Engineering":
    st.subheader("Process Engineering / Improvement Records")
    amap = asset_options()
    materials = store.get("settings", {}).get("materials", ["Glass", "Silon", "Alumina", "Quartz"])
    with st.form("process_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Improvement / process title")
        department = c2.text_input("Department")
        material = c3.selectbox("Material", [""] + materials + ["Other"])
        d1, d2, d3 = st.columns(3)
        product = d1.text_input("Product / family")
        selected_asset = d2.selectbox("Machine / asset", [""] + list(amap.keys()))
        business_id = d3.text_input("Existing / future process ID (optional)")
        baseline = st.text_area("Current process / baseline")
        problem = st.text_area("Problem / opportunity")
        change = st.text_area("Proposed / implemented change")
        e1, e2, e3, e4 = st.columns(4)
        old_cycle = e1.number_input("Old cycle time (min)", min_value=0.0, step=0.1)
        new_cycle = e2.number_input("New cycle time (min)", min_value=0.0, step=0.1)
        old_reject = e3.number_input("Old rejection %", min_value=0.0, step=0.1)
        new_reject = e4.number_input("New rejection %", min_value=0.0, step=0.1)
        validation = st.text_area("Validation / evidence / conclusion")
        submitted = st.form_submit_button("Add Process Improvement", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Process title is required.")
        else:
            reduction = ((old_cycle - new_cycle) / old_cycle * 100) if old_cycle else 0.0
            r = base_record("process_improvement", title, department, business_id, "")
            r.update({"material": material, "product": product, "asset_uuid": amap.get(selected_asset, ""), "baseline": baseline, "problem": problem, "change": change, "old_cycle_time_min": float(old_cycle), "new_cycle_time_min": float(new_cycle), "cycle_time_reduction_pct": reduction, "old_rejection_pct": float(old_reject), "new_rejection_pct": float(new_reject), "validation": validation})
            add_record("process_improvements", r)
            st.rerun()

    if store["process_improvements"]:
        df = records_dataframe(store["process_improvements"])
        show = [c for c in ["business_id", "department", "material", "product", "title", "old_cycle_time_min", "new_cycle_time_min", "cycle_time_reduction_pct"] if c in df.columns]
        st.dataframe(df[show], use_container_width=True, hide_index=True)

elif page == "Engineering Trials":
    st.subheader("Engineering Trials / Experimental Records")
    materials = store.get("settings", {}).get("materials", ["Glass", "Silon", "Alumina", "Quartz"])
    amap = asset_options()
    with st.form("trial_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Trial title")
        department = c2.text_input("Department")
        material = c3.selectbox("Material", [""] + materials + ["Other"])
        d1, d2, d3 = st.columns(3)
        product = d1.text_input("Product / family")
        selected_asset = d2.selectbox("Machine / asset", [""] + list(amap.keys()))
        business_id = d3.text_input("Trial / legacy ID (optional)")
        objective = st.text_area("Objective / hypothesis")
        parameters = st.text_area("Parameters / setup / tooling")
        results = st.text_area("Results / measurements")
        conclusion = st.selectbox("Conclusion", ["Pending", "Successful", "Partial", "Failed", "Inconclusive"])
        recommendation = st.text_area("Recommendation / next step")
        submitted = st.form_submit_button("Add Engineering Trial", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Trial title is required.")
        else:
            r = base_record("engineering_trial", title, department, business_id, "")
            r.update({"material": material, "product": product, "asset_uuid": amap.get(selected_asset, ""), "objective": objective, "parameters": parameters, "results": results, "conclusion": conclusion, "recommendation": recommendation})
            add_record("trials", r)
            st.rerun()
    if store["trials"]:
        st.dataframe(records_dataframe(store["trials"]), use_container_width=True, hide_index=True)

elif page == "Machinery & Tooling Research":
    st.subheader("Machinery & Tooling Research")
    with st.form("research_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Research title")
        department = c2.text_input("Department")
        research_type = c3.selectbox("Research type", ["Machine", "Tooling", "Fixture", "Process Technology", "Supplier", "Other"])
        requirement = st.text_area("Problem / requirement")
        constraints = st.text_area("Technical requirements / constraints")
        candidates = st.text_area("Candidates considered")
        findings = st.text_area("Findings / comparison")
        recommendation = st.text_area("Recommendation / justification")
        business_id = st.text_input("Research / project ID (optional)")
        submitted = st.form_submit_button("Add Research Record", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Research title is required.")
        else:
            r = base_record("engineering_research", title, department, business_id, "")
            r.update({"research_type": research_type, "requirement": requirement, "constraints": constraints, "candidates": candidates, "findings": findings, "recommendation": recommendation})
            add_record("research", r)
            st.rerun()
    if store["research"]:
        st.dataframe(records_dataframe(store["research"]), use_container_width=True, hide_index=True)

elif page == "RCA & Investigations":
    st.subheader("Root Cause Analysis & Engineering Investigations")
    amap = asset_options()
    with st.form("rca_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Investigation title")
        department = c2.text_input("Department")
        selected_asset = c3.selectbox("Asset (optional)", [""] + list(amap.keys()))
        problem = st.text_area("What happened?")
        expected = st.text_area("What should have happened?")
        containment = st.text_area("Immediate containment")
        evidence = st.text_area("Evidence / observations")
        why1 = st.text_input("Why 1")
        why2 = st.text_input("Why 2")
        why3 = st.text_input("Why 3")
        why4 = st.text_input("Why 4")
        why5 = st.text_input("Why 5")
        root_cause = st.text_area("Root cause")
        corrective = st.text_area("Corrective action")
        preventive = st.text_area("Preventive action")
        verification = st.text_area("Effectiveness verification")
        business_id = st.text_input("RCA / legacy ID (optional)")
        submitted = st.form_submit_button("Add Investigation", use_container_width=True)
    if submitted:
        if not title.strip():
            st.error("Investigation title is required.")
        else:
            r = base_record("rca", title, department, business_id, "")
            r.update({"asset_uuid": amap.get(selected_asset, ""), "problem": problem, "expected": expected, "containment": containment, "evidence": evidence, "five_whys": [why1, why2, why3, why4, why5], "root_cause": root_cause, "corrective_action": corrective, "preventive_action": preventive, "verification": verification})
            add_record("rca", r)
            st.rerun()
    if store["rca"]:
        st.dataframe(records_dataframe(store["rca"]), use_container_width=True, hide_index=True)

elif page == "System Data & Backup":
    st.subheader("System Data, Configuration & Backup")
    settings = store.setdefault("settings", {})
    company_name = st.text_input("Company name (optional)", value=settings.get("company_name", ""))
    departments_text = st.text_area("Departments (one per line)", value="\n".join(settings.get("departments", [])))
    materials_text = st.text_area("Materials (one per line)", value="\n".join(settings.get("materials", [])))
    if st.button("Save Configuration"):
        settings["company_name"] = company_name.strip()
        settings["departments"] = [x.strip() for x in departments_text.splitlines() if x.strip()]
        settings["materials"] = [x.strip() for x in materials_text.splitlines() if x.strip()]
        st.success("Configuration updated in the current session.")

    st.divider()
    st.markdown("### Local persistence")
    st.caption("The hosted app does not deliberately persist your engineering records. Download the system JSON regularly and load it again when returning to the app.")
    st.download_button("Download Complete System JSON", data=store_bytes(store), file_name="Process_and_Maintenance_Engineering_System.json", mime="application/json", use_container_width=True)
    st.download_button("Download Local Backup ZIP", data=backup_zip(store), file_name="Process_and_Maintenance_Engineering_System_Backup.zip", mime="application/zip", use_container_width=True)
    st.download_button("Download Engineering Management Summary PDF", data=generate_summary_pdf(store), file_name="Engineering_Management_Summary.pdf", mime="application/pdf", use_container_width=True)

    st.markdown("### Record counts")
    counts = {k: len(store.get(k, [])) for k in ["assets", "actions", "maintenance", "process_improvements", "trials", "research", "rca"]}
    st.dataframe(pd.DataFrame([counts]), use_container_width=True, hide_index=True)

st.divider()
st.caption("Data model rule: hidden system UUIDs maintain relationships. Business IDs, department IDs, legacy IDs and aliases are optional and can be added or changed later without breaking linked records.")
