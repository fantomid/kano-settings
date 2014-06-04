#!/usr/bin/env python

# set_advance.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano.gtk3.kano_dialog as kano_dialog
import kano_settings.set_advance.password as password
import kano_settings.components.fixed_size_box as fixed_size_box
from ..config_file import get_setting, set_setting
from kano.utils import run_cmd
from kano.logging import set_system_log_level

win = None
update = None
box = None

parental = False
debug = False
CONTAINER_HEIGHT = 70


def activate(_win, _box, _update):
    global update, box, win

    win = _win
    box = _box
    update = _update
    update.set_sensitive(False)
    read_config()

    title = Heading("Advance options", "Toggle parental lock and debug mode")
    box.pack_start(title.container, False, False, 0)

    # Contains main buttons
    settings = fixed_size_box.Fixed()

    box.pack_start(settings.box, False, False, 0)

    vertical_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=40)
    vertical_container.set_valign(Gtk.Align.CENTER)

    # Parental lock check button
    parental_button = Gtk.CheckButton("Parental lock")
    parental_button.set_can_focus(False)
    parental_button.props.valign = Gtk.Align.CENTER
    parental_button.connect("clicked", on_parental_toggled)

    # Check parental option appropriately
    active_item = get_setting("Parental-lock")
    parental_button.set_active(active_item)

    vertical_container.pack_start(parental_button, False, False, 0)

    # Debug mode check button
    debug_button = Gtk.CheckButton("Debug mode")
    debug_button.set_can_focus(False)
    debug_button.props.valign = Gtk.Align.CENTER
    debug_button.connect("clicked", on_debug_toggled)

    # Check debug option appropriately
    active_item = get_setting("Debug-mode")
    debug_button.set_active(active_item)

    vertical_container.pack_start(debug_button, False, False, 0)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - CONTAINER_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(vertical_container)
    settings.box.pack_start(valign, False, False, 0)

    # Add apply changes button under the main settings content
    box.pack_start(update.align, False, False, 0)


def to_password(arg1=None, arg2=None):
    global win, box, update

    # Remove children
    for i in box.get_children():
        box.remove(i)

    password.activate(win, box, update)


def apply_changes(button):

    # Change on parental-lock
    if (get_setting("Parental-lock") != parental):
        print "Change to password"

    # Change on debug mode
    new_debug = get_setting("Debug-mode")
    if new_debug != debug:
        # Activate debug mode
        if new_debug == 0:
            set_system_log_level("debug")
            msg = "Activated"
        # De-activate debug mode
        else:
            set_system_log_level("error")
            msg = "De-activated"

        kdialog = kano_dialog.KanoDialog("Debug mode", msg)
        kdialog.run()

    update_config()
    update.set_sensitive(False)


def read_config():
    global mode, mode_index, parental, debug

    parental = get_setting("Parental-lock")
    debug = get_setting("Debug-mode")


def update_config():
    # Add new configurations to config file.
    set_setting("Parental-lock", parental)
    set_setting("Debug-mode", debug)


# Returns True if all the entries are the same as the ones stored in the config file.
def compare():
    # Compare new entries to old ones already stored.
    display_parental = (get_setting("Parental-lock") == parental)
    display_debug = (get_setting("Debug-mode") == debug)
    return display_debug and display_parental


def on_parental_toggled(button):
    global parental, update

    parental = int(button.get_active())
    update.set_sensitive(True)
    to_password()

def on_debug_toggled(button):
    global debug, update

    debug = int(button.get_active())
    update.set_sensitive(True)
