import subprocess
from pathlib import Path
import datetime as dt


#Base zenity helpers----------------
def zenity_list(prompt,options):
    cmd =[
        "zenity", "--list", "--radiolist",
        "--title=Study Logger",
        f"--text={prompt}",
        "--column=Pick", "--column=Option",
        "--width=400", "--height=300"
    
    ]
    for i, opt in enumerate(options):
        cmd += ["TRUE" if i == 0 else "FALSE",opt]
    try:
        out=subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except subprocess.CalledProcessError:
        return None

def zenity_entry(prompt, default=""):
    try:
        out = subprocess.check_output(
            [
                "zenity", "--entry",
                "--title=Study Logger",
                f"--text={prompt}",
                "--entry-text", default,
                "--width=400"

            ],
            stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except subprocess.CalledProcessError:
        return None
    
def zenity_question(prompt,ok="yes", cancel="No"):
    try:
        subprocess.check_call(
            [
                "zenity","--question",
                "--title=Study Logger",
                f"--text={prompt}",
                f"--ok-label={ok}",
                f"--cancel-label={cancel}",
                "--width=400"

            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False
    
def zenity_info(message):
    try:
        subprocess.Popen(
            [
                "zenity", "--info",
                "--title=Study Logger",
                f"--text={message}",
                "--width=400"
            
            ]
        )
    except Exception:
        pass


