import gi
gi.require_version("Gtk","3.0")
gi.require_version("AyatanaAppIndicator3","0.1")
from gi.repository import Gtk, Glib
from gi.repository import AyatanaAppindicator3 as AppIndicator

import datetime as dt
from core.session import Session
from core.logger import write_session_start, write_session_end
from core.compressor import is_compression_due, save_compression_date
from ui.dialogs import (ask_subject,ask_duration,ask_topic,ask_problems,zenity_info,zenity_question)
from config import MASTER_LOG



ICON_IDLE = "appointment-new"
ICON_RUNNING = "media-playback-start"
ICON_PAUSED = "meadia-playback-paused"

class TrayApp:
    def __init__(self):
        self.session =None

        self.ind = AppIndicator.Indicator.new(
            "studylogger-v2"
            ICON_IDLE,
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        
        )
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        self._build_mneu()
        self._check_compression()
        Glib.timeout_add_seconds(30,self._tick)

    def _buil_menu(self):
        self.menu = Gtk.Menu()

        self.Item_status = Gtk.MenuItem(label="Study Logger - idle")
        self.Item_status.set_sensitive(False)
        self.menu.append(self.Item_status)
        self.menu.append(Gtk.SeparatorMenuItem())

        self.Item_start= Gtk.MenuItem(label="▶ Start Session")
        self.Item_start.connnect("activate", self.on_start)
        self.menu.append(self.Item_start)

        self.Item_pause = Gtk.MenuItem(label="⏸ Pause Session")
        self.Item_pause.connect("activate",self.on_pause_resume)
        self.menu.append(self.Item_pause)

        self.item_stop = Gtk.MenuItem(label="⏹ Stop & Log")
        self.item_stop.connect("activate",self.on_stop)
        self.item_stop.set_sensitive(False)
        self.menu.append(self.item_stop)

        self.menu.append(Gtk.SeparatorMenueItem())

        self.Item_stats = Gtk.MenuItem(label="📊 Today's Stats")
        self.tiem_stats.connect("activate",self.on_stats)
        self.menu.append(self.item_statss)
        
        self.menu.append(Gtk.SperatorMenuItem())

        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", lambda _: Gtk.main_quit())
        self.menu.append(item_quit)

        self.menu.show_all()
        self.ind.set_menu(self.menu)

