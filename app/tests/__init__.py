# app/tests/api/__init__.py

import pytest
import sys
import os

# Add the root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))