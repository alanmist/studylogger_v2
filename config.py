from pathlib import Path

#-----Path-------------------------
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

DAILY_DIR = LOGS_DIR / "daily"
MASTER_LOG = LOGS_DIR / "master_log.md"
COMPRESSED_DIR = LOGS_DIR / "compressed"
STATE_FILE = Path.home() / ".local/share/studylogger_v2_state.json"

#Subject--------------------------------
SUBJECTS = ["Math", "Physics", "Coding", "Computer Science", "Proofreading", "other"]

#Session Defualts------------------------------
DEFAULT_DURATION_MIN = 120

#Monthly compression---------------------------
COMPRESSION_REMINDER_DAYS = 30

