import subprocess
import sys
from pathlib import Path

from comparator import summary_stats
from engineering_system import blank_store, dashboard_metrics, load_store, maintenance_kpis, store_bytes


def test_application_imports():
    import advanced_operations  # noqa: F401
    import control_centre  # noqa: F401
    import engineering_system  # noqa: F401
    import next_layer  # noqa: F401
    import production_readiness  # noqa: F401
    import supplier_contacts  # noqa: F401


def test_engineering_calculations_and_dashboard_metrics():
    store = blank_store()
    assert dashboard_metrics(store)["assets"] == 0
    assert maintenance_kpis(store)["breakdown_count"] == 0


def test_comparator_functionality():
    result = summary_stats("N10 G01 X1\nN20 M30", "N10 G01 X1\nN20 M02")
    assert result["matching_lines"] == 1
    assert result["differences"] == 1


def test_safe_serialization_round_trip():
    restored = load_store(store_bytes(blank_store()))
    assert restored["schema"] == "process-maintenance-engineering-system"
    assert restored["version"] == 2


def test_side_effect_free_imports():
    repo = Path(__file__).resolve().parents[1]
    modules = "engineering_system next_layer advanced_operations control_centre production_readiness supplier_contacts comparator setup_sheet".split()
    code = "\n".join(f"import {module}" for module in modules) + "\nprint('IMPORT_OK')"
    result = subprocess.run([sys.executable, "-c", code], cwd=repo, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith("IMPORT_OK")
    assert "Local URL" not in result.stdout
