"""
Utility Functions - Logging, evidence saving, and reporting
"""

import cv2
import datetime
import os
import json
from pathlib import Path

# Create directories if they don't exist
EVIDENCE_DIR = "evidence"
LOGS_DIR = "logs"
STATS_DIR = "stats"

for directory in [EVIDENCE_DIR, LOGS_DIR, STATS_DIR]:
    Path(directory).mkdir(exist_ok=True)

# Log levels
LOG_LEVELS = {
    "DEBUG": "🔵",
    "INFO": "🟢",
    "WARNING": "🟡",
    "CRITICAL": "🔴",
}

def get_timestamp():
    """Return formatted timestamp"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_filename_timestamp():
    """Return timestamp suitable for filenames"""
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]

def format_message(msg_type="default"):
    """Format different message types"""
    timestamps = {
        "timestamp": get_timestamp(),
        "filename": get_filename_timestamp(),
    }
    return timestamps.get(msg_type, get_timestamp())

def save_evidence(frame, alert_type="UNKNOWN"):
    """
    Save frame as evidence image
    
    Args:
        frame: OpenCV frame/image to save
        alert_type: Type of alert (FIRE, PROXIMITY, MANUAL, DEBUG)
        
    Returns:
        str: Filename of saved evidence or None if failed
    """
    try:
        if frame is None:
            print("❌ Cannot save evidence: Frame is empty")
            return None
        
        timestamp = get_filename_timestamp()
        filename = f"{EVIDENCE_DIR}/evidence_{alert_type}_{timestamp}.jpg"
        
        success = cv2.imwrite(filename, frame)
        
        if success:
            print(f"📸 Evidence saved: {filename}")
            return filename
        else:
            print(f"❌ Failed to save evidence: {filename}")
            return None
            
    except Exception as e:
        print(f"❌ Error saving evidence: {str(e)}")
        return None

def log_event(message, level="INFO"):
    """
    Log event to file and console
    
    Args:
        message (str): Event message
        level (str): Log level (DEBUG, INFO, WARNING, CRITICAL)
    """
    try:
        timestamp = get_timestamp()
        level_icon = LOG_LEVELS.get(level, "📝")
        
        # Format log message
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # Print to console
        print(f"{level_icon} {log_message}")
        
        # Write to log file
        log_file = f"{LOGS_DIR}/alerts_log.txt"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
        
        # Also maintain a CSV for statistics
        if level == "CRITICAL":
            save_to_csv(message, level)
            
    except Exception as e:
        print(f"❌ Error logging event: {str(e)}")

def save_to_csv(message, level):
    """Save critical events to CSV for analysis"""
    try:
        import csv
        
        csv_file = f"{STATS_DIR}/alerts_statistics.csv"
        
        # Check if file exists
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(["Timestamp", "Level", "Message"])
            
            writer.writerow([get_timestamp(), level, message])
            
    except Exception as e:
        print(f"⚠️  Error saving to CSV: {str(e)}")

def print_system_info():
    """Print system setup information"""
    print("\n" + "="*60)
    print("📋 SYSTEM INFORMATION")
    print("="*60)
    print(f"Evidence Directory: {os.path.abspath(EVIDENCE_DIR)}")
    print(f"Logs Directory: {os.path.abspath(LOGS_DIR)}")
    print(f"Stats Directory: {os.path.abspath(STATS_DIR)}")
    print(f"OpenCV Version: {cv2.__version__}")
    print("="*60 + "\n")

def print_help():
    """Print help information"""
    print("\n" + "="*70)
    print("🆘 KEYBOARD CONTROLS")
    print("="*70)
    print("Q          - Quit the application")
    print("S          - Display statistics")
    print("C          - Capture manual screenshot (saved as evidence)")
    print("="*70)
    print("\n📌 ALERTS:")
    print("  🔥 FIRE DETECTED      - Fire flame color detected in frame")
    print("  ⚠️  PROXIMITY ALERT   - Fire detected within 150px of person")
    print("  🚨 CRITICAL           - Potential safety hazard")
    print("="*70 + "\n")

def get_statistics():
    """Read and return statistics from CSV"""
    try:
        stats_file = f"{STATS_DIR}/alerts_statistics.csv"
        
        if not os.path.isfile(stats_file):
            print("❌ No statistics available yet")
            return None
        
        with open(stats_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if len(lines) <= 1:
            print("ℹ️  No alerts recorded yet")
            return None
        
        print(f"\n📊 Total Alerts Logged: {len(lines) - 1}")
        print("\nRecent Alerts:")
        print("-" * 70)
        
        for line in lines[-11:-1]:  # Show last 10 alerts
            print(line.strip())
        
        print("-" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading statistics: {str(e)}")
        return None