#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

Path("backups").mkdir(exist_ok=True)

devices = ["Core-Switch-01", "Edge-Router-01", "Access-Switch-Floor2"]

for device in devices:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backups/{device}_{timestamp}.cfg"
    
    config = f"""!
version 15.1
hostname {device}
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
!
end
# Backup created: {timestamp}
"""
    with open(filename, "w") as f:
        f.write(config)
    print(f"✅ Created: {filename}")

print("\n📊 Demo backups created!")
