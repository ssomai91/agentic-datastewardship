"""Test-side access to the shared schema registry in tools/schema_support.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from schema_support import (  # noqa: E402,F401
    REGISTRY,
    SCHEMAS,
    all_schema_paths,
    build_registry,
    load,
    validator_for,
)