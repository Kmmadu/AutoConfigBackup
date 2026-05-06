#!/usr/bin/env python3
"""Restore a configuration to a device from backup"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.backup import restore_device_config
from src.utils import load_devices
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python3 restore_cli.py <backup_filename>")
    print("Example: python3 restore_cli.py backups/Core-Switch-01_20260506_160540.cfg")
    sys.exit(1)

backup_file = sys.argv[1]
backup_path = Path(backup_file)

if not backup_path.exists():
    print(f"❌ Backup file not found: {backup_file}")
    sys.exit(1)

# Extract device name from filename
device_name = backup_path.stem.split('_')[0]

# Find device in inventory
devices = load_devices()
target_device = None
for device in devices:
    if device.get('name') == device_name:
        target_device = device
        break

if not target_device:
    print(f"❌ Device '{device_name}' not found in inventory")
    print("Available devices:")
    for device in devices:
        print(f"  - {device.get('name', device['host'])}")
    sys.exit(1)

# Get credentials
username = os.getenv("DEVICE_USERNAME")
password = os.getenv("DEVICE_PASSWORD")

if not username or not password:
    print("❌ Credentials not found in .env file")
    sys.exit(1)

print(f"⚠️  WARNING: This will replace the ENTIRE configuration on {device_name}")
print(f"   Backup file: {backup_file}")
print(f"   Device IP: {target_device['host']}")
print()
confirm = input("Type 'RESTORE' to continue: ")

if confirm != "RESTORE":
    print("Restore cancelled")
    sys.exit(0)

print(f"\n🔄 Restoring {device_name} from {backup_file}...")
result = restore_device_config(target_device, backup_path, username, password)

if result['success']:
    print(f"\n✅ {result['message']}")
else:
    print(f"\n❌ {result['message']}")
