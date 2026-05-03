from pathlib import Path

#-----Path-------------------------
BASE_DIR = Path(__file__).parent

ASSETS_DIR = BASE_DIR / "assets"
#OBSIDIAN VAULT PATH--------------------
VAULT_ROOT =Path("/home/alanmist/Documents/Obsidian/Polymath_Journey/Logs")
LOGS_DIR = VAULT_ROOT
DAILY_DIR = VAULT_ROOT / "Daily"
MASTER_LOG = VAULT_ROOT/ "Master_log.md"
COMPRESSED_DIR = VAULT_ROOT/ "Compressed"


STATE_FILE = Path.home() / ".local/share/studylogger_v2_state.json"




#Subject--------------------------------
SUBJECTS = ["Math", "Physics", "Coding", "Computer Science", "Proofreading", "other"]

#Session Defualts------------------------------
DEFAULT_DURATION_MIN = 120

#Monthly compression---------------------------
COMPRESSION_REMINDER_DAYS = 30

