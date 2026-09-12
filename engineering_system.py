import io
import json
import uuid
import zipfile
from copy import deepcopy
from datetime import date, datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

SCHEMA = "process-maintenance-engineering-system"
VERSION = 1

MODULES = [
    "assets",
    "actions",
    "maintenance",
    "process_improvements",
    "trials",
    "research",
    "rca",
]


def now_iso():
    return datetime.now().replace(microsecond=0).isoformat()


def new_uuid():
    return str(uuid.uuid4())


def blank_store():
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "settings": {
            "company_name": "",
            "departments": [],
            "materials": ["Glass", "Silon", "Alumina", "Quartz"],
        },
        "assets": [],
        "actions": [],
        "maintenance": [],
        "process_improvements": [],
        "trials": [],
        "research": [],
        "rca": [],
    }


def normalise_store(store):
    base = blank_store()
    out = deepcopy(store) if isinstance(store, dict) else {}
    if out.get("schema") != SCHEMA:
        raise ValueError("This is not a Process and Maintenance Engineering System JSON file.")
    base.update(out)
    base.setdefault("settings", {})
    base["settings"].setdefault("company_name", "")
    base["settings"].setdefault("departments", [])
    base["settings"].setdefault("materials", ["Glass", "Silon", "Alumina", "Quartz"])
    for module in MODULES:
        base.setdefault(module, [])
    return base


def store_bytes(store):
    payload = deepcopy(store)
    payload["updated_at"] = now_iso()
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def load_store(file_bytes):
    return normalise_store(json.loads(file_bytes.decode("utf-8")))


def base_record(record_type, title="", department="", business_id="", legacy_id=""):
    return {
        "system_uuid": new_uuid(),
        "record_type": record_type,
        "title": title.strip(),
        "department": department.strip(),
        "business_id": business_id.strip(),
        "legacy_id": legacy_id.strip(),
        "alias": "",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }


def record_label(record):
    human = record.get("business_id") or record.get("legacy_id") or record.get("alias")
    prefix = f"{human} - " if human else ""
    return f"{prefix}{record.get('title','Untitled')}"


def asset_map(store):
    return {a.get("system_uuid"): a for a in store.get("assets", [])}


def asset_label_by_uuid(store, asset_uuid):
    asset = asset_map(store).get(asset_uuid)
    return record_label(asset) if asset else ""


def dashboard_metrics(store):
    actions = store.get("actions", [])
    maintenance = store.get("maintenance", [])
    assets = store.get("assets", [])
    open_actions = [a for a in actions if a.get("status", "Open") not in ["Complete", "Closed"]]
    critical = [a for a in open_actions if a.get("priority") == "Critical"]
    breakdowns = [m for m in maintenance if m.get("maintenance_type") == "Breakdown"]
    downtime = sum(float(m.get("downtime_hours", 0) or 0) for m in breakdowns)
    due_pm = [m for m in maintenance if m.get("maintenance_type") == "Preventive" and m.get("status") in ["Due", "Overdue"]]
    return {
        "assets": len(assets),
        "open_actions": len(open_actions),
        "critical_actions": len(critical),
        "breakdowns": len(breakdowns),
        "downtime_hours": downtime,
        "due_pm": len(due_pm),
    }


def records_dataframe(records):
    if not records:
        return pd.DataFrame()
    rows = []
    for r in records:
        row = dict(r)
        for key, value in list(row.items()):
            if isinstance(value, (list, dict)):
                row[key] = json.dumps(value, ensure_ascii=False)
        rows.append(row)
    return pd.DataFrame(rows)


def _table(data):
    table = Table(data, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#25313c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def generate_summary_pdf(store):
    metrics = dashboard_metrics(store)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=12*mm, rightMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], alignment=TA_CENTER, fontSize=20)
    story = [
        Spacer(1, 30*mm),
        Paragraph("Process and Maintenance Engineering System", title),
        Paragraph("Engineering Management Summary", ParagraphStyle("sub", parent=styles["Heading2"], alignment=TA_CENTER)),
        Spacer(1, 8*mm),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ParagraphStyle("date", parent=styles["Normal"], alignment=TA_CENTER)),
        PageBreak(),
    ]
    summary = [
        ["Metric", "Value"],
        ["Assets", metrics["assets"]],
        ["Open Engineering Actions", metrics["open_actions"]],
        ["Critical Open Actions", metrics["critical_actions"]],
        ["Breakdown Records", metrics["breakdowns"]],
        ["Recorded Breakdown Downtime (h)", f"{metrics['downtime_hours']:.2f}"],
        ["Preventive Maintenance Due/Overdue", metrics["due_pm"]],
    ]
    story += [Paragraph("System Overview", styles["Heading2"]), _table(summary), Spacer(1, 8*mm)]

    action_rows = [["Priority", "Status", "Department", "Title", "Owner", "Due"]]
    for r in store.get("actions", [])[:40]:
        action_rows.append([
            r.get("priority", ""), r.get("status", ""), r.get("department", ""),
            r.get("title", ""), r.get("owner", ""), r.get("due_date", "")
        ])
    if len(action_rows) > 1:
        story += [Paragraph("Engineering Actions", styles["Heading2"]), _table(action_rows), PageBreak()]

    maint_rows = [["Type", "Status", "Department", "Asset", "Date", "Downtime h", "Summary"]]
    for r in store.get("maintenance", [])[:50]:
        maint_rows.append([
            r.get("maintenance_type", ""), r.get("status", ""), r.get("department", ""),
            asset_label_by_uuid(store, r.get("asset_uuid", "")), r.get("event_date", ""),
            r.get("downtime_hours", 0), r.get("title", "")
        ])
    if len(maint_rows) > 1:
        story += [Paragraph("Maintenance / Breakdown Summary", styles["Heading2"]), _table(maint_rows)]

    doc.build(story)
    return buffer.getvalue()


def backup_zip(store):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Process_Maintenance_Engineering_System.json", store_bytes(store))
        zf.writestr("README.txt", "Local backup for Process and Maintenance Engineering System.\nThe JSON file contains all current records.\n")
    return out.getvalue()
