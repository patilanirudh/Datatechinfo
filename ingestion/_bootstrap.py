"""Adds backend/ to sys.path so ingestion scripts can reuse the backend's models,
db session, and TomTom client instead of duplicating them. Import this first."""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
