import subprocess


from config import SUBJECTS

import gi

gi.require_version("Gtk", "3.0")


from gi.repository import Gtk

SLIP_CAUSES = {
    "Math": [
        "Concept gap",
        "Arithmetic slip",
        "Misread the problem",
        "Rushed",
        "Focus broke",
    ],
    "Physics": [
        "Concept gap",
        "Arithmetic slip",
        "Misread the problem",
        "Rushed",
        "Focus broke",
    ],
    "Coding": [
        "Concept gap",
        "Syntax error",
        "Didn't understand the API",
        "Debugging took too long",
        "Scope creep",
        "Focus broke",
    ],
    "Proofs": [
        "Concept gap",
        "Logic error",
        "Misread the problem",
        "Rushed",
        "Focus broke",
    ],
}


# Base zenity helpers----------------
def zenity_list(prompt, options):
    cmd = [
        "zenity",
        "--list",
        "--radiolist",
        "--title=Study Logger",
        f"--text={prompt}",
        "--column=Pick",
        "--column=Option",
        "--width=400",
        "--height=300",
    ]
    for i, opt in enumerate(options):
        cmd += ["TRUE" if i == 0 else "FALSE", opt]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except subprocess.CalledProcessError:
        return None


def zenity_entry(prompt, default=""):
    try:
        out = subprocess.check_output(
            [
                "zenity",
                "--entry",
                "--title=Study Logger",
                f"--text={prompt}",
                "--entry-text",
                default,
                "--width=400",
            ],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except subprocess.CalledProcessError:
        return None


def zenity_question(prompt, ok="yes", cancel="No"):
    try:
        subprocess.check_call(
            [
                "zenity",
                "--question",
                "--title=Study Logger",
                f"--text={prompt}",
                f"--ok-label={ok}",
                f"--cancel-label={cancel}",
                "--width=400",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def zenity_info(message):
    try:
        subprocess.Popen(
            [
                "zenity",
                "--info",
                "--title=Study Logger",
                f"--text={message}",
                "--width=400",
            ]
        )
    except Exception:
        pass


# -----session start dialogs---------


def ask_subject():
    return zenity_list("What are you studing?", SUBJECTS)


def ask_duration():
    result = zenity_entry("How many minutes?", "120")
    if result is None:
        return None
    if not result.isdigit():
        zenity_info("Please enter a number.")
        return None
    value = int(result)
    if value <= 0:
        zenity_info("minutes must be more than 0.")
        return None
    return value


def ask_topic(subject):
    return zenity_entry(f"What exactly are you studying in {subject}?", "")


def ask_completed():
    return zenity_question("Did you complete your study goal?")


def ask_extend_minutes():
    if not zenity_question("Do you want to extend the session?"):
        return None

    result = zenity_entry("How many more minutes?", "30")
    if result is None:
        return None
    if not result.isdigit():
        zenity_info("Please enter a number")
        return None
    value = int(result)
    if value <= 0:
        zenity_info("Minutes must be more than 0")
        return None
    return value


# Gtk Problem capture dialog-----------


class ProblemCaptureDialog(Gtk.Dialog):
    def __init__(self, subject):
        super().__init__(title=f"Session Log -{subject}")
        self.set_default_size(500, 600)

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)

        # What did you work on
        box.pack_start(Gtk.Label(label="What did you work on:"), False, False, 0)
        self.work_on = Gtk.TextView()
        self.work_on.set_wrap_mode(Gtk.WrapMode.WORD)
        work_on_scroll = Gtk.ScrolledWindow()
        work_on_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        work_on_scroll.set_size_request(-1, 80)
        work_on_scroll.add(self.work_on)
        box.pack_start(work_on_scroll, False, False, 0)

        # What did you get right
        box.pack_start(Gtk.Label(label="What did you get right:"), False, False, 0)
        self.get_right = Gtk.TextView()
        self.get_right.set_wrap_mode(Gtk.WrapMode.WORD)
        get_right_scroll = Gtk.ScrolledWindow()
        get_right_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        get_right_scroll.set_size_request(-1, 80)
        get_right_scroll.add(self.get_right)
        box.pack_start(get_right_scroll, False, False, 0)

        # Where did you slip + Category
        self.cause_combo = Gtk.ComboBoxText()
        causes = SLIP_CAUSES.get(subject, SLIP_CAUSES["Math"])
        for cause in causes:
            self.cause_combo.append_text(cause)
        self.cause_combo.set_active(0)
        box.pack_start(Gtk.Label(label="Where did you slip :"), False, False, 0)
        box.pack_start(Gtk.Label(label="Cause:"), False, False, 0)
        box.pack_start(self.cause_combo, False, False, 0)
        self.slip_wehere = Gtk.TextView()
        self.slip_wehere.set_wrap_mode(Gtk.WrapMode.WORD)
        slip_wehere_scroll = Gtk.ScrolledWindow()
        slip_wehere_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        slip_wehere_scroll.set_size_request(-1, 80)
        slip_wehere_scroll.add(self.slip_wehere)
        box.pack_start(slip_wehere_scroll, False, False, 0)

        # one thing you don't understand
        box.pack_start(
            Gtk.Label(label="One thing you don't understand:"), False, False, 0
        )
        self.dont_understand = Gtk.TextView()
        self.dont_understand.set_wrap_mode(Gtk.WrapMode.WORD)
        dont_understand_scroll = Gtk.ScrolledWindow()
        dont_understand_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        dont_understand_scroll.set_size_request(-1, 80)
        dont_understand_scroll.add(self.dont_understand)
        box.pack_start(dont_understand_scroll, False, False, 0)

        # Frist 10 minuts next session/Tought
        box.pack_start(
            Gtk.Label(label="First 10 minuts next session/Thought:"), False, False, 0
        )
        self.tought = Gtk.TextView()
        self.tought.set_wrap_mode(Gtk.WrapMode.WORD)
        tought_scroll = Gtk.ScrolledWindow()
        tought_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        tought_scroll.set_size_request(-1, 80)
        tought_scroll.add(self.tought)
        box.pack_start(tought_scroll, False, False, 0)

        # Buttons
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Save session", Gtk.ResponseType.OK)
        self.show_all()

    def get_text(self, textview):
        buf = textview.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True).strip()

    def get_results(self):
        return {
            "work_on": self.get_text(self.work_on),
            "get_right": self.get_text(self.get_right),
            "slip_where": self.get_text(self.slip_wehere),
            "dont_understand": self.get_text(self.dont_understand),
            "next_session": self.get_text(self.tought),
            "cause": self.cause_combo.get_active_text(),
        }


def ask_problems(subject):
    dialog = ProblemCaptureDialog(subject)
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        results = dialog.get_results()
        dialog.destroy()
        return results
    dialog.destroy()
    return None
