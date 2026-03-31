"""
pytest configuration for root tests directory.

NOTE: Do NOT put global sys.modules mocks here.
If you need to mock heavy dependencies for specific tests,
use pytest fixtures with monkeypatch instead.
"""

import sys
import os

# Ensure backend is on path for all tests
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
