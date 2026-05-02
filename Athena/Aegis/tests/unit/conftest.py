"""Pytest configuration."""

import sys
from pathlib import Path

# Add Athena to path
athena_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(athena_path))