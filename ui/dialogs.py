import subprocess
from pathlib import Path
import datetime as dt
from config import SUBJECTS, ASSETS_DIR
import os
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
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




#-----session start dialogs---------

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
    if value <=0:
        zenity_info("minutes must be more than 0.")
        return None
    return value

def ask_topic(subject):
    return zenity_entry(f"What exactly are you studying in {subject}?","")

#Gtk Problem capture dialog-----------

class ProblemCaptureDialog(Gtk.Dialog):
    def __init__(self, subject):
        super().__init__(title=f"Session End -{subject}")
        self.set_default_size(500,600)
        self.images = {"solved": [], "attempted":[], "couldnt_start":[]}

        box =self.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)

        #completed?
        self.completed_check = Gtk.CheckButton(label="I Completed my goal")
        box.pack_start(self.completed_check, False,False,0)

        #problems Solved
        box.pack_start(Gtk.Label(label="problems Solved:"),False,False,0)
        self.solved_text = Gtk.TextView()
        self.solved_text.set_size_request(-1,80)
        box.pack_start(self.solved_text,False,False,0)
        btn_box_solved = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        btn_solved = Gtk.Button(label="📎 Paste from clipboard")
        btn_solved.connect("clicked", self.paste_image, "solved")
        btn_browse_solved = Gtk.Button(label="📁 Browse file")
        btn_browse_solved.connect("clicked", self.browse_image, "solved")
        btn_box_solved.pack_start(btn_solved, True, True, 0)
        btn_box_solved.pack_start(btn_browse_solved, True, True, 0)
        box.pack_start(btn_box_solved, False, False, 0)
        
        
        #Problem attempted
        box.pack_start(Gtk.Label(label="Problems Attempted:"), False, False,0)
        self.attempted_text = Gtk.TextView()
        self.attempted_text.set_size_request(-1,80)
        box.pack_start(self.attempted_text,False,False,0)
        btn_box_attempted= Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        btn_attempted = Gtk.Button(label="📎 Paste from clipboard")
        btn_attempted.connect("clicked", self.paste_image, "attempted")
        btn_browse_attempted = Gtk.Button(label="📁 Browse file")
        btn_browse_attempted.connect("clicked", self.browse_image, "attempted")
        btn_box_attempted.pack_start(btn_attempted, True, True, 0)
        btn_box_attempted.pack_start(btn_browse_attempted, True, True, 0)
        box.pack_start(btn_box_attempted, False, False, 0)

        # Couldn't start
        box.pack_start(Gtk.Label(label="Couldn't Start:"), False, False, 0)
        self.couldnt_text = Gtk.TextView()
        self.couldnt_text.set_size_request(-1, 80)
        box.pack_start(self.couldnt_text, False, False, 0)
        btn_box_couldnt = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        btn_couldnt= Gtk.Button(label="📎 Paste from clipboard")
        btn_couldnt.connect("clicked", self.paste_image, "couldnt_start")
        btn_browse_couldnt= Gtk.Button(label="📁 Browse file")
        btn_browse_couldnt.connect("clicked", self.browse_image, "couldnt_start")
        btn_box_couldnt.pack_start(btn_couldnt, True, True, 0)
        btn_box_couldnt.pack_start(btn_browse_couldnt, True, True, 0)
        box.pack_start(btn_box_couldnt, False, False, 0)


        # Reflection
        box.pack_start(Gtk.Label(label="Reflection / thoughts:"), False, False, 0)
        self.reflection_text = Gtk.TextView()
        self.reflection_text.set_size_request(-1, 80)
        box.pack_start(self.reflection_text, False, False, 0)

        # Buttons
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Save session", Gtk.ResponseType.OK)
        self.show_all()
    def paste_image(self,button, section):
        clipboard =Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        pixbuf= clipboard.wait_for_image()
        if pixbuf is None:
            zenity_info("No image in clipboard. Take a screenshot first.")
            return
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = ASSETS_DIR / f"{timestamp}_{section}.png"
        pixbuf.savev(str(filename),"png",[],[])
        self.images[section].append(filename)
        zenity_info(f"Image saved for {section}!")

    def get_text(self, textview):
        buf =textview.get_buffer()
        return buf.get_text(buf.get_start_iter(),buf.get_end_iter(),True).strip()
    
    def get_results(self):
        return{
            "completed":self.completed_check.get_active(),
            "solved":self.get_text(self.solved_text),
            "attempted": self.get_text(self.attempted_text),
            "couldnt_start":self.get_text(self.couldnt_text),
            "reflection": self.get_text(self.reflection_text),
            "images":self.images
        }
    def browse_image(self, button, section):
        dialog = Gtk.FileChooserDialog(
            title="Select image",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Select", Gtk.ResponseType.OK)
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/jpeg")
        dialog.add_filter(filter_img)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = Path(dialog.get_filename())
            self.images[section].append(filename)
            zenity_info(f"Image added for {section}!")
        dialog.destroy()

def ask_problems(subject):
    dialog =ProblemCaptureDialog(subject)
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        results= dialog.get_results()
        dialog.destroy()
        return results
    dialog.destroy()
    return None

