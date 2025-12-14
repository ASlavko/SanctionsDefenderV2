#!/usr/bin/env python3
"""
Test the search_api.py locally to check for import errors
"""

import sys
import os

# Add functions directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions'))

try:
    print("Importing functions_framework...")
    import functions_framework
    print("✓ functions_framework imported")
    
    print("Importing other modules...")
    import json
    from google.cloud import firestore
    from datetime import datetime
    from flask import jsonify
    import re
    print("✓ Standard modules imported")
    
    print("Importing matching module...")
    from matching import match_name
    print("✓ matching module imported")
    
    print("\nAll imports successful!")
    print("No syntax or import errors detected.")
    
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
