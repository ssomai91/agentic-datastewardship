"""Test-side access to tools/handoff_checks.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from handoff_checks import handoff_reference_problems  # noqa: E402,F401