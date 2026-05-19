import datetime as dt
from config import DAILY_DIR, MASTER_LOG


def ensure_dirs():
    DAILY_DIR.mkdir(parents=True, exist_ok=True)


def get_daily_path():
    today = dt.datetime.now().strftime("%Y-%m-%d")
    return DAILY_DIR / f"{today}.md"


def _ensure_master_log_date_heading():
    today = dt.datetime.now().strftime("%Y-%m-%d")
    heading = f"# {today}"
    if MASTER_LOG.exists():
        text = MASTER_LOG.read_text()
        if heading in text.splitlines():
            return
    with open(MASTER_LOG, "a") as f:
        f.write(f"\n{heading}\n")


def write_session_start(session):
    ensure_dirs()
    daily = get_daily_path()

    if not daily.exists():
        daily.write_text(f"# {dt.datetime.now().strftime('%Y-%m-%d')}\n\n")

    _ensure_master_log_date_heading()

    header = (
        f"\n## {session.subject} - {session.start_time.strftime('%H:%M')}\n"
        f"**Topic:** {session.topic}\n"
        f"**Planned:** {session.planned_minutes} minutes\n"
        f"**Status:** In progress\n\n"
        f"---\n"
    )

    with open(daily, "a") as f:
        f.write(header)
    with open(MASTER_LOG, "a") as f:
        f.write(header)


def write_session_end(
    session,
    work_on,
    got_right,
    slip_where,
    dont_understand,
    next_session,
    cause,
    completed,
):
    daily = get_daily_path()

    actual_min = session.actual_study_minutes()
    paused_min = int(round(session.pause_accum_sec / 60))

    block = (
        f"\n**Status:** {'Completed' if completed else 'Not completed'}\n"
        f"**Actual study time:** {actual_min} minutes\n"
        f"**Paused:** {paused_min} minutes\n\n"
        f"### What I worked on\n{work_on or 'None'}\n\n"
        f"### What I  got right\n{got_right or 'None'}\n\n"
        f"### Where I slipped\n**Cause:** {cause or 'None'}\n{slip_where or 'None'}\n\n"
        f"### One thing I don't understand\n{dont_understand or 'None'}\n\n"
        f"### Next session - first 10 minutes\n{next_session or 'None'}\n\n"
        f"---\n"
    )

    with open(daily, "a") as f:
        f.write(block)
    with open(MASTER_LOG, "a") as f:
        f.write(block)
