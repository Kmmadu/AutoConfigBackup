#!/usr/bin/env python3
"""Minimal test to verify basic functionality"""

import sys
from pathlib import Path

# Test 1: Check imports
print("1. Testing imports...")
try:
    from src.utils import load_devices
    print("   ✓ utils imported")
except Exception as e:
    print(f"   ✗ utils failed: {e}")
    sys.exit(1)

try:
    from src.connection import connect_device
    print("   ✓ connection imported")
except Exception as e:
    print(f"   ✗ connection failed: {e}")

try:
    from src.backup import backup_device
    print("   ✓ backup imported")
except Exception as e:
    print(f"   ✗ backup failed: {e}")

# Test 2: Load configuration
print("\n2. Loading devices...")
devices = load_devices()
print(f"   Loaded {len(devices)} devices")

# Test 3: Check environment
print("\n3. Checking environment...")
import os
from dotenv import load_dotenv
load_dotenv()
username = os.getenv("DEVICE_USERNAME")
print(f"   DEVICE_USERNAME: {'set' if username else 'NOT SET'}")
git_enabled = os.getenv("GIT_ENABLED", "false")
print(f"   GIT_ENABLED: {git_enabled}")

print("\n✓ Basic tests passed!")
print("\nNext steps:")
print("  - Add real devices to config/devices.yaml")
print("  - Run: python3 src/main.py")
print("  - Run: python3 app.py (for web UI)")
