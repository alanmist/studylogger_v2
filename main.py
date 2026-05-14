import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os
from ui.tray import TrayApp


def main():
    os.system("pkill -f 'python.*main.py' 2>/dev/null")
    print("creating TrayApp...")
    app = TrayApp()

    print("starting gtk.main()...")
    Gtk.main()
    print("Gtk.main()end")


if __name__ == "__main__":
    main()
