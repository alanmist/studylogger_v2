import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import Gtk, GLib
from gi.repository import AyatanaAppIndicator3 as AppIndicator

import datetime as dt
from core.session import Session
from core.logger import write_session_start, write_session_end
from core.compressor import is_compression_due, save_compression_date
from ui.dialogs import (ask_subject,ask_duration,ask_topic,ask_problems,
                        zenity_info, zenity_question)

from config import MASTER_LOG

ICON_IDLE = "appointment-new"
ICON_RUNNING = "media-playback-start"
ICON_PAUSED = "media-playback-pause"

class TrayApp:
    def __init__(self):
        self.session = None

        self.ind = AppIndicator.Indicator.new(
            "studylogger-v2",
            ICON_IDLE,
            AppIndicator.IndicatorCategory.APPLICATION_STATUS   
        )
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        self._build_menu()
        self._check_compression()
        GLib.timeout_add_seconds(30,self._tick)

    def _build_menu(self):
        self.menu = Gtk.Menu()

        self.item_status = Gtk.MenuItem(label= "Study logger -idle")
        self.item_status.set_sensitive(False)
        self.menu.append(self.item_status)
        self.menu.append(Gtk.SeparatorMenuItem())

        self.item_start = Gtk.MenuItem(label ="▶ Start Session")
        self.item_start.connect("activate", self.on_start)
        self.menu.append(self.item_start)

        self.item_pause =  Gtk.MenuItem(label= "⏸ Pause Session")
        self.item_pause.connect("activate",self.on_pause_resume)
        self.item_pause.set_sensitive(False)
        self.menu.append(self.item_pause)

        self.item_stop = Gtk.MenuItem(label= "⏹ Stop & Log")
        self.item_stop.connect("activate",self.on_stop)
        self.item_stop.set_sensitive(False)
        self.menu.append(self.item_stop)

        self.menu.append(Gtk.SeparatorMenuItem())

        self.item_stats =Gtk.MenuItem(label="📊 Today's Stats")
        self.item_stats.connect("activate",self.on_stats)
        self.menu.append(self.item_stats)
        
        self.menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label ="Quit")
        item_quit.connect("activate", lambda _: Gtk.main_quit())
        self.menu.append(item_quit)

        self.menu.show_all()
        self.ind.set_menu(self.menu)
        

    def _update_menu(self):
        if self.session is None:
            self.item_status.set_label("Study Logger - idle")
            self.item_start.set_sensitive(True)
            self.item_pause.set_sensitive(False)
            self.item_stop.set_sensitive(False)
            self.ind.set_icon_full(ICON_IDLE,"idle")
        elif self.session.paused:
            left = self.session.remaining_at_pause_min or 0
            self.item_status.set_label(f"⏸ {self.session.subject}: {left}m left (paused)")
            self.item_start.set_sensitive(False)
            self.item_pause.set_label("▶ Resume Session")
            self.item_pause.set_sensitive(True)
            self.item_stop.set_sensitive(True)
            self.ind.set_icon_full(ICON_IDLE, "Paused")
        else:
            left = max(0,int((self.session.planned_end-dt.datetime.now().astimezone()).total_seconds()//60))
            self.item_status.set_label(f"▶ {self.session.subject}: {left}m left")
            self.item_start.set_sensitive(False)
            self.item_pause.set_label("⏸ Pause Session")
            self.item_pause.set_sensitive(True)
            self.item_stop.set_sensitive(True)
            self.ind.set_icon_full(ICON_RUNNING,"running")

    def _tick(self):
        self._update_menu()
        if self.session and not self.session.paused:
            if dt.datetime.now().astimezone() >= self.session.planned_end:
                self._end_session()
        return True
    
    def _check_compression(self):
        if is_compression_due():
            zenity_info(
                "⚠️ Monthly compression is due!\n"
                "Please send your master log to Claude\n"
                "and compress before starting a new session."
            )

    def on_start(self, *_):
        subject =ask_subject()
        if subject is None:
            return
        duration = ask_duration()
        if duration is None:
            return
        topic = ask_topic(subject)
        if topic is None:
            return
        
        self.session = Session(subject,topic,duration)
        write_session_start(self.session)
        self._update_menu()
        zenity_info(f"Session started!\n{subject} - {topic}\n{duration} minutes")

    def on_pause_resume(self, *_):
        if self.session is None:
            return
        if self.session.paused:
            self.session.resume()
            zenity_info("Session resumed.")
            self._update_menu()
        else:
            self.session.pause()
            zenity_info("Session Paused.")
            self._update_menu()
    
    def on_stop(self,*_):
        if self.session is None:
            return
        self._end_session()

    def on_stats(self,*_):
        today = dt.datetime.now().strftime("%Y-%m-%d")
        total =0
        try:
            with open(MASTER_LOG,"r") as f:
                for line in f:
                    if "Actual study time:" in line and today in"":
                        parts =line.split(":")
                        if len(parts)>1:
                            mins =parts[1].strip().split()[0]
                            if mins.isdigit():
                                total +=int(mins)
        
        except Exception:
            pass
        zenity_info(f"Today's total study time: ~{total} minutes")
    def _end_session(self):
        if self.session is None:
            return
        subject = self.session.subject
        results = ask_problems(subject)
        if results is None:
            return
        write_session_end(
            self.session,
            results.get("solved",""),
            results.get("attempted", ""),
            results.get("couldnt_start", ""),
            results.get("reflection", ""),
            results.get("completed", False)
        )
        self.session = None
        self._update_menu()
        zenity_info("Session logged successfully!")


