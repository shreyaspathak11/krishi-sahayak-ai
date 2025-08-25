"""
Configuration import wrapper for knowledge_base module.

This module provides a clean way to import configuration without path manipulation.
"""

import sys
from pathlib import Path

# Only add to path if not already available
try:
    from app.config import *
except ImportError:
    # Fallback: add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from app.config import *

# Re-export for clean imports

