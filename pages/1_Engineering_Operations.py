from datetime import date, timedelta
import pandas as pd
import streamlit as st

from engineering_system import blank_store, base_record, by_uuid, record_label, asset_label_by_uuid, pm_status, parse_date
from next_layer import (
    update_record, complete_pm, create_action_from_breakdown, create_rca_from_breakdown,
    create_pm_from_template, spare_stock_status, low_stock_spares, asset_history,
)

st.set_page_config(page_title="Engineering Operations", page_icon="🔧", layout="wide")
if "pm_store" not in st.session_state:
    st.session_state.pm_store = blank_store()
store = st.session_state.pm_store
store.setdefault("pm_templates", [])

def options(module):
    return {record_label(r): r.get("system_uuid") for r in store.get(module, [])}

def show(rows, empty="No records."):
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info(empty)

st.title("Engineering Operations")
st.caption("Operational layer for PM execution, machine-specific templates, breakdown follow-up, spare stock control, record editing and linked asset history.")

tabs = st.tabs(["Asset History", "PM Execution", "PM Templates", "Breakdown Follow-up", "Spare Stock", "Record Editor"])

with tabs[0]:
    st.subheader("Linked Asset Engineering History")
    amap=options("assets")
    if not amap:
        st.info("Create assets in the main Asset Register first.")
    else:
        name=st.selectbox("Asset",list(amap),key="hist_asset")
        uid=amap[name]
        asset=by_uuid(store["assets"])[uid]
        c=st.columns(4)
        c[0].metric("Department",asset.get("department","—"))
        c[1].metric("Class",asset.get("asset_class","—"))
        c[2].metric("Criticality",asset.get("criticality","—"))
        c[3].metric("Status",asset.get("status","—"))
        history=asset_history(store,uid)
        show(history,"No engineering history linked to this asset yet.")
        st.markdown("#### Maintenance history")
        show([{"Date":r.get("event_date"),"Type":r.get("maintenance_type"),"Status":r.get("status"),"Downtime h":r.get("downtime_hours",0),"Repair h":r.get("repair_hours",0),"Summary":r.get("title")} for r in store.get("maintenance",[]) if r.get("asset_uuid")==uid],"No maintenance history.")
        st.markdown("#### PM schedules")
        show([{"Status":pm_status(r),"Task":record_label(r),"Frequency":r.get("frequency"),"Next due":r.get("next_due_date"),"Last completed":r.get("last_completed_date",""),"Owner":r.get("owner")} for r in store.get("pm_schedules",[]) if r.get("asset_uuid")==uid],"No PM schedules linked to this asset.")

with tabs[1]:
    st.subheader("Complete Preventive Maintenance")
    pmmap=options("pm_schedules")
    if not pmmap:
        st.info("No PM schedules exist yet.")
    else:
        selected=st.selectbox("PM schedule",list(pmmap),key="exec_pm")
        uid=pmmap[selected]
        pm=by_uuid(store["pm_schedules"])[uid]
        c=st.columns(5)
        c[0].metric("Status",pm_status(pm))
        c[1].metric("Asset",asset_label_by_uuid(store,pm.get("asset_uuid")) or "—")
        c[2].metric("Frequency",pm.get("frequency","—"))
        c[3].metric("Next due",pm.get("next_due_date","—"))
        c[4].metric("Last complete",pm.get("last_completed_date","—"))
        st.markdown("**Checklist / standard work**")
        st.write(pm.get("checklist") or "No checklist recorded.")
        if pm.get("safety_requirements"):
            st.warning(pm.get("safety_requirements"))
        with st.form("complete_pm_form"):
            a=st.columns(3)
            completed=a[0].date_input("Completion date",date.today())
            technician=a[1].text_input("Completed by",pm.get("owner",""))
            hours=a[2].number_input("Actual labour hours",0.0,step=.25)
            notes=st.text_area("Work completed / findings")
            parts=st.text_area("Parts / consumables used")
            confirm=st.checkbox("I confirm this PM has been completed")
            submit=st.form_submit_button("Complete PM & Calculate Next Due",use_container_width=True)
        if submit:
            if not confirm:
                st.error("Confirm completion before closing the PM.")
            else:
                _,nxt=complete_pm(store,uid,completed,technician,notes,hours,parts)
                st.success(f"PM completed. Next due: {nxt.isoformat() if nxt else 'manual scheduling required'}")
                st.rerun()

with tabs[2]:
    st.subheader("Machine-Specific PM Templates")
    classes=store.get("settings",{}).get("asset_classes",[])
    with st.form("new_pm_template",clear_on_submit=True):
        a=st.columns(3)
        title=a[0].text_input("Template / PM task")
        asset_class=a[1].selectbox("Asset class",[""]+classes)
        frequency=a[2].selectbox("Frequency",["Daily","Weekly","Monthly","Quarterly","6 Monthly","Annual","Custom"])
        b=st.columns(3)
        custom=b[0].number_input("Custom interval days",0,step=1)
        owner=b[1].text_input("Default responsible role")
        hours=b[2].number_input("Estimated labour hours",0.0,step=.25)
        checklist=st.text_area("Checklist / standard work")
        safety=st.text_area("Safety / isolation requirements")
        parts=st.text_area("Required parts / consumables")
        reference=st.text_area("OEM / internal maintenance reference")
        save=st.form_submit_button("Save PM Template",use_container_width=True)
    if save and title.strip():
        r=base_record("pm_template",title,"")
        r.update({"asset_class":asset_class,"frequency":frequency,"custom_interval_days":int(custom),"owner":owner,"estimated_hours":float(hours),"checklist":checklist,"safety_requirements":safety,"required_parts":parts,"reference":reference})
        store["pm_templates"].append(r)
        st.rerun()

    tmap=options("pm_templates"); amap=options("assets")
    if tmap:
        show([{"Template":record_label(r),"Asset Class":r.get("asset_class"),"Frequency":r.get("frequency"),"Owner":r.get("owner"),"Estimated h":r.get("estimated_hours",0)} for r in store["pm_templates"]])
    if tmap and amap:
        st.markdown("#### Apply template to an asset")
        with st.form("apply_pm_template"):
            a=st.columns(4)
            t=a[0].selectbox("Template",list(tmap))
            asset=a[1].selectbox("Asset",list(amap))
            due=a[2].date_input("First due date",date.today())
            owner=a[3].text_input("Owner override")
            apply=st.form_submit_button("Create PM Schedule from Template",use_container_width=True)
        if apply:
            template=by_uuid(store["pm_templates"])[tmap[t]]
            machine=by_uuid(store["assets"])[amap[asset]]
            if template.get("asset_class") and machine.get("asset_class") and template.get("asset_class") != machine.get("asset_class"):
                st.warning(f"Template class is {template.get('asset_class')} but selected asset is {machine.get('asset_class')}. Schedule created as requested.")
            create_pm_from_template(store,tmap[t],amap[asset],due,owner)
            st.success("PM schedule created.")
            st.rerun()

with tabs[3]:
    st.subheader("Breakdown Follow-up")
    breakdowns=[r for r in store.get("maintenance",[]) if r.get("maintenance_type")=="Breakdown"]
    bmap={record_label(r):r.get("system_uuid") for r in breakdowns}
    if not bmap:
        st.info("No breakdown records available.")
    else:
        selected=st.selectbox("Breakdown",list(bmap))
        uid=bmap[selected]
        r=by_uuid(store["maintenance"])[uid]
        c=st.columns(4)
        c[0].metric("Asset",asset_label_by_uuid(store,r.get("asset_uuid")) or "—")
        c[1].metric("Date",r.get("event_date","—"))
        c[2].metric("Downtime",f"{float(r.get('downtime_hours',0) or 0):.2f} h")
        c[3].metric("Status",r.get("status","—"))
        st.write("**Symptoms:**",r.get("symptom",""))
        st.write("**Diagnosis:**",r.get("diagnosis",""))
        st.write("**Work completed:**",r.get("action_taken",""))
        st.caption(f"Linked actions: {len(r.get('linked_action_uuids',[]))} · Linked RCA records: {len(r.get('linked_rca_uuids',[]))}")
        a,b=st.columns(2)
        with a:
            owner=st.text_input("Action owner",r.get("owner",""),key="bd_action_owner")
            due=st.date_input("Action due",date.today()+timedelta(days=7),key="bd_action_due")
            if st.button("Create Linked Engineering Action",use_container_width=True):
                create_action_from_breakdown(store,uid,owner,due)
                st.success("Engineering action created and linked.")
                st.rerun()
        with b:
            rca_owner=st.text_input("RCA owner",r.get("owner",""),key="bd_rca_owner")
            if st.button("Create Linked RCA",use_container_width=True):
                create_rca_from_breakdown(store,uid,rca_owner)
                st.success("RCA created and linked.")
                st.rerun()

with tabs[4]:
    st.subheader("Spare Parts Stock Control")
    warnings=low_stock_spares(store)
    c=st.columns(3)
    c[0].metric("Stock warnings",len(warnings))
    c[1].metric("Out of stock",len([s for s in warnings if spare_stock_status(s)=="Out of Stock"]))
    c[2].metric("Low stock",len([s for s in warnings if spare_stock_status(s)=="Low Stock"]))
    show([{"Status":spare_stock_status(s),"Part":record_label(s),"Asset":asset_label_by_uuid(store,s.get("asset_uuid")),"On Hand":s.get("quantity_on_hand",0),"Minimum":s.get("minimum_stock",0),"Lead Days":s.get("lead_time_days",0),"Location":s.get("storage_location","")} for s in store.get("spares",[])],"No spare parts records.")
    smap=options("spares")
    if smap:
        selected=st.selectbox("Update spare stock",list(smap))
        uid=smap[selected]; s=by_uuid(store["spares"])[uid]
        with st.form("edit_spare_stock"):
            a=st.columns(3)
            qty=a[0].number_input("Quantity on hand",0.0,step=1.0,value=float(s.get("quantity_on_hand",0) or 0))
            minimum=a[1].number_input("Minimum stock",0.0,step=1.0,value=float(s.get("minimum_stock",0) or 0))
            location=a[2].text_input("Storage location",s.get("storage_location",""))
            save=st.form_submit_button("Save Stock Details")
        if save:
            update_record(store,"spares",uid,{"quantity_on_hand":float(qty),"minimum_stock":float(minimum),"storage_location":location})
            st.rerun()

with tabs[5]:
    st.subheader("Record Editor")
    editable=["assets","actions","maintenance","pm_schedules","process_improvements","trials","research","rca","products","tooling","spares"]
    module=st.selectbox("Record type",editable,format_func=lambda x:x.replace("_"," ").title())
    rmap=options(module)
    if not rmap:
        st.info("No records in this module.")
    else:
        selected=st.selectbox("Record",list(rmap),key="editor_record")
        uid=rmap[selected]; r=by_uuid(store[module])[uid]
        with st.form("basic_editor"):
            a=st.columns(3)
            title=a[0].text_input("Title / name",r.get("title",""))
            dept=a[1].text_input("Department",r.get("department",""))
            business=a[2].text_input("Business / current ID",r.get("business_id",""))
            b=st.columns(2)
            legacy=b[0].text_input("Legacy ID",r.get("legacy_id",""))
            alias=b[1].text_input("Alias",r.get("alias",""))
            save=st.form_submit_button("Save Record Identity",use_container_width=True)
        if save:
            update_record(store,module,uid,{"title":title,"department":dept,"business_id":business,"legacy_id":legacy,"alias":alias})
            st.success("Record updated.")
            st.rerun()
        st.caption(f"System UUID: {uid}")
        st.json(r,expanded=False)
