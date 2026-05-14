import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os
import sys
from ui.tray import TrayApp

LOCK_FILE = "/tmp/studylogger.lock"


def main():

    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE) as f:
            old_pid = f.read().strip()
        if old_pid:
            os.system(f"kill {old_pid} 2>/dev/null")

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    print("creating TrayApp...")
    app = TrayApp()

    print("starting gtk.main()...")
    Gtk.main()
    print("Gtk.main()end")


if __name__ == "__main__":
    main()
