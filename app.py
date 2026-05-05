from flask import Flask, render_template
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_devices
from src.main import run_single_backup

app = Flask(__name__)

@app.route('/')
def dashboard():
    devices = load_devices()
    return render_template('dashboard.html', devices=devices)

@app.route('/devices')
def devices_page():
    devices = load_devices()
    return render_template('devices.html', devices=devices)

@app.route('/history')
def history():
    from datetime import datetime
    backup_dir = Path("backups")
    backups = []
    if backup_dir.exists():
        for file in sorted(backup_dir.glob("*.cfg"), reverse=True):
            backups.append({
                'filename': file.name,
                'size': f"{file.stat().st_size / 1024:.1f} KB",
                'modified': datetime.fromtimestamp(file.stat().st_mtime)
            })
    return render_template('history.html', backups=backups)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
