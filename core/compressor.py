import json
import datetime as dt
from pathlib import Path
from config import COMPRESSION_REMINDER_DAYS, MASTER_LOG


COMPRESSION_STATE = Path.home() / ".local/share/studylogger_compression.json"

def get_last_compression_date():
    if not COMPRESSION_STATE.exists():
        return None
    
    try:
        data = json.loads(COMPRESSION_STATE.read_text())
        return dt.date.fromisoformat(data["last_compressed"])
    except Exception:
        return None
    

def save_compression_date():
    COMPRESSION_STATE.parent.mkdir(parents=True, exist_ok=True)
    COMPRESSION_STATE.write_text(json.dumps({"last_compressed":dt.date.today().isoformat()}))


def is_compression_due():
    last = get_last_compression_date()
    if last is None:
        return False
    days_passed = (dt.date.today() - last).days
    return days_passed >= COMPRESSION_REMINDER_DAYS


def get_master_log_size():
    if not MASTER_LOG.exists():
        return 0
    return MASTER_LOG.stat().st_size


if __name__ == "__main__":
    print(f"Last compression: {get_last_compression_date()}")
    print(f"Compression due: {is_compression_due()}")
    print(f"Master log size: {get_master_log_size()} bytes")
    
    print("\nSaving compression date as today...")
    save_compression_date()
    
    print(f"Last compression: {get_last_compression_date()}")
    print(f"Compression due: {is_compression_due()}")