"""Ensures the project root is importable so tests can use `from src...`."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
