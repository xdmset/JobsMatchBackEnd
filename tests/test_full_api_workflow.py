from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_full_api_workflow_script_passes():
    result = subprocess.run(
        [sys.executable, str(ROOT / "TESTMIKE" / "full_api_flow_check.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"full_api_flow_check.py failed with code {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "full_api_flow_check: OK" in result.stdout
