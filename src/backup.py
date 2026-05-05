import logging
import os
from pathlib import Path
from datetime import datetime
from difflib import unified_diff

from src.connection import connect_device

logger = logging.getLogger(__name__)

def backup_device(device: dict, username: str, password: str, git_enabled: bool = True) -> dict:
    """
    Back up a single device's running configuration.
    
    Args:
        device: Device dictionary with host, device_type, etc.
        username: SSH username
        password: SSH password
        git_enabled: Whether to commit to Git
    
    Returns:
        dict: {
            'success': bool,
            'changed': bool,
            'diff': str or None,
            'error': str or None,
            'backup_file': str or None
        }
    """
    hostname = device.get("name", device["host"])
    result = {
        'success': False,
        'changed': False,
        'diff': None,
        'error': None,
        'backup_file': None
    }
    
    # Prepare connection parameters
    device_params = {
        'device_type': device['device_type'],
        'host': device['host'],
        'username': username,
        'password': password,
    }
    if 'secret' in device and device['secret']:
        device_params['secret'] = device['secret']
    
    # Connect to device
    conn = connect_device(device_params, retries=2)
    if not conn:
        result['error'] = "Failed to connect after retries"
        return result
    
    try:
        # Get running config
        logger.info(f"Retrieving running-config from {hostname}")
        running_config = conn.send_command("show running-config")
        
        # Save backup
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{hostname}_{timestamp}.cfg"
        filepath = backup_dir / filename
        
        with open(filepath, "w") as f:
            f.write(running_config)
        
        result['backup_file'] = str(filepath)
        result['success'] = True
        logger.info(f"Backup saved: {filepath}")
        
        # Check for changes against previous backup
        previous_backup = find_previous_backup(hostname)
        if previous_backup:
            with open(previous_backup, "r") as f:
                previous_config = f.read()
            
            if running_config.strip() != previous_config.strip():
                result['changed'] = True
                # Generate diff
                diff_lines = list(unified_diff(
                    previous_config.splitlines(),
                    running_config.splitlines(),
                    fromfile=f"{hostname}_previous",
                    tofile=f"{hostname}_current",
                    lineterm=''
                ))
                result['diff'] = '\n'.join(diff_lines[:50])  # First 50 lines only
                logger.warning(f"Configuration CHANGE detected for {hostname}")
            else:
                logger.info(f"No configuration change for {hostname}")
        
        # Git operations
        if git_enabled and result['success']:
            git_commit_and_push(commit_message=f"Backup {hostname} - {timestamp}")
        
    except Exception as e:
        logger.error(f"Backup failed for {hostname}: {e}")
        result['error'] = str(e)
    finally:
        conn.disconnect()
    
    return result

def find_previous_backup(device_name: str) -> Path | None:
    """Find the most recent backup file for a device"""
    backup_dir = Path("backups")
    backups = sorted(backup_dir.glob(f"{device_name}_*.cfg"), reverse=True)
    
    if len(backups) >= 2:
        return backups[1]  # Second most recent (skip the one we just saved)
    elif len(backups) == 1:
        return backups[0]  # Only one backup exists
    return None

# Import git function to avoid circular import
from src.utils import git_commit_and_push