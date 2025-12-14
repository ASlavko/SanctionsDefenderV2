#!/usr/bin/env python3
import subprocess
import json

# Use firebase CLI to read Firestore
result = subprocess.run([
    'firebase', 'firestore:documents', 'list', 
    '--collection-path=import_sessions',
    '--project=sanction-defender-firebase'
], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print("\nReturn code:", result.returncode)
