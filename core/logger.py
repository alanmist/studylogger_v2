from pathlib import Path
import datetime as dt
from config import DAILY_DIR, MASTER_LOG


def ensure_dirs():
    DAILY_DIR.mkdir(parents=True, exist_ok=True)


def get_daily_path():
    today = dt.datetime.now().strftime("%Y-%m-%d")
    return DAILY_DIR / f"{today}.md"


def write_session_start(session):
    ensure_dirs()
    daily = get_daily_path()

    if not daily.exists():
        daily.write_text(f"# {dt.datetime.now().strftime('%Y-%m-%d')}\n\n")

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
    problems_solved,
    problems_attempted,
    problems_couldnt_start,
    reflection,
    completed,
    images=None,
):
    daily = get_daily_path()

    actual_min = session.actual_study_minutes()
    paused_min = int(round(session.pause_accum_sec / 60))
    if images is None:
        images = {"solved": [], "attempted": [], "couldnt_start": []}

    def format_section(text, image_list):
        parts = []
        if text:
            parts.append(text)
        if image_list:
            for img_path in image_list:
                parts.append(f"![[{img_path.name}]]")
        if not parts:
            return None
        return "\n\n".join(parts)

    block = (
        f"\n**Status:** {'Completed' if completed else 'Not completed'}\n"
        f"**Actual study time:** {actual_min} minutes\n"
        f"**Paused:** {paused_min} minutes\n\n"
        f"### Problems Solved\n{format_section( problems_solved,images.get("solved",[]))}\n\n"
        f"### Problems Attempted\n{format_section(problems_attempted,images.get("attempted",[]))}\n\n"
        f"### Couldn't Start\n{format_section(problems_couldnt_start,images.get("coulndt_start",[]))}\n\n"
        f"### Reflection\n{reflection or 'None'}\n\n"
        f"---\n"
    )

    with open(daily, "a") as f:
        f.write(block)
    with open(MASTER_LOG, "a") as f:
        f.write(block)
