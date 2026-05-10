import subprocess


from config import SUBJECTS

import gi

gi.require_version("Gtk", "3.0")


from gi.repository import Gtk


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


# Gtk Problem capture dialog-----------


class ProblemCaptureDialog(Gtk.Dialog):
    def __init__(self, subject):
        super().__init__(title=f"Session End -{subject}")
        self.set_default_size(500, 600)

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)

        # completed?
        self.completed_check = Gtk.CheckButton(label="I Completed my goal")
        box.pack_start(self.completed_check, False, False, 0)

        # problems Solved
        box.pack_start(Gtk.Label(label="problems Solved:"), False, False, 0)
        self.solved_text = Gtk.TextView()
        self.solved_text.set_wrap_mode(Gtk.WrapMode.WORD)
        solved_scroll = Gtk.ScrolledWindow()
        solved_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        solved_scroll.set_size_request(-1, 80)
        solved_scroll.add(self.solved_text)
        box.pack_start(solved_scroll, False, False, 0)

        # Problem attempted
        box.pack_start(Gtk.Label(label="Problems Attempted:"), False, False, 0)
        self.attempted_text = Gtk.TextView()
        self.attempted_text.set_wrap_mode(Gtk.WrapMode.WORD)
        attempted_scroll = Gtk.ScrolledWindow()
        attempted_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        attempted_scroll.set_size_request(-1, 80)
        attempted_scroll.add(self.attempted_text)
        box.pack_start(attempted_scroll, False, False, 0)

        # Couldn't start
        box.pack_start(Gtk.Label(label="Couldn't Start:"), False, False, 0)
        self.couldnt_text = Gtk.TextView()
        self.couldnt_text.set_wrap_mode(Gtk.WrapMode.WORD)
        couldnt_scroll = Gtk.ScrolledWindow()
        couldnt_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        couldnt_scroll.set_size_request(-1, 80)
        couldnt_scroll.add(self.couldnt_text)
        box.pack_start(couldnt_scroll, False, False, 0)

        # Reflection
        box.pack_start(Gtk.Label(label="Reflection / thoughts:"), False, False, 0)
        self.reflection_text = Gtk.TextView()
        self.reflection_text.set_wrap_mode(Gtk.WrapMode.WORD)
        reflection_scroll = Gtk.ScrolledWindow()
        reflection_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        reflection_scroll.set_size_request(-1, 80)
        reflection_scroll.add(self.reflection_text)
        box.pack_start(reflection_scroll, False, False, 0)

        # Buttons
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Save session", Gtk.ResponseType.OK)
        self.show_all()

    def get_text(self, textview):
        buf = textview.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True).strip()

    def get_results(self):
        return {
            "completed": self.completed_check.get_active(),
            "solved": self.get_text(self.solved_text),
            "attempted": self.get_text(self.attempted_text),
            "couldnt_start": self.get_text(self.couldnt_text),
            "reflection": self.get_text(self.reflection_text),
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
