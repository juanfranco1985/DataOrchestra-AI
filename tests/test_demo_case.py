from pathlib import Path
import shutil

from dataorchestra.cli import run_analysis, run_preflight


def test_demo_case_can_run_preflight_and_analysis(tmp_path: Path):
    source = Path(__file__).resolve().parents[1] / "demos" / "retail_santa_clara"
    demo_dir = tmp_path / "retail_santa_clara"
    shutil.copytree(source, demo_dir)

    preflight = run_preflight(demo_dir)
    analysis = run_analysis(demo_dir)

    assert preflight["status"] == "ready_for_analysis"
    assert analysis["status"] == "analysis_done"
    assert analysis["alerts"]
    assert (demo_dir / "reports" / "diagnostico_borrador.html").exists()
