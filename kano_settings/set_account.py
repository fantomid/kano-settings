#!/usr/bin/env python
#
# account.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the UI of the account setting

from gi.repository import Gtk, Gdk, GObject
import threading
import os

from kano.gtk3.heading import Heading
import kano.gtk3.kano_dialog as kano_dialog
from kano.gtk3.buttons import KanoButton
from kano.gtk3.labelled_entries import LabelledEntries
from kano_world.functions import has_token

from kano.utils import get_user_unsudoed, ensure_dir
from kano_settings.templates import TopBarTemplate, Template
from kano_settings.data import get_data
import kano.utils as utils
import pam


ADD_REMOVE_USER_PATH = '/tmp/kano-init/add-remove'


class SetAccount(TopBarTemplate):
    data = get_data("SET_ACCOUNT")

    def __init__(self, win):
        TopBarTemplate.__init__(self)

        self.win = win
        self.win.set_main_widget(self)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        self.added_or_removed_account = False

        main_title = self.data["LABEL_1"]
        main_description = self.data["LABEL_2"]
        accounts_title = self.data["LABEL_1"]
        accounts_description = self.data["LABEL_2"]
        add_text = self.data["ADD_BUTTON"]
        remove_text = self.data["REMOVE_BUTTON"]
        pass_text = self.data["PASSWORD_BUTTON"]

        main_heading = Heading(main_title, main_description)

        self.pass_button = KanoButton(pass_text)
        self.pass_button.pack_and_align()
        self.pass_button.connect("button-release-event", self.go_to_password_screen)

        self.add_button = KanoButton(add_text)
        self.add_button.set_size_request(200, 44)
        self.add_button.connect("button-release-event", self.add_account)

        self.remove_button = KanoButton(remove_text, color="red")
        self.remove_button.set_size_request(200, 44)
        self.remove_button.connect("button-release-event", self.remove_account_dialog)

        button_container = Gtk.Box()
        button_container.pack_start(self.add_button, False, False, 10)
        button_container.pack_start(self.remove_button, False, False, 10)

        button_align = Gtk.Alignment(xscale=0, xalign=0.5)
        button_align.add(button_container)

        accounts_heading = Heading(accounts_title, accounts_description)

        # Check if we already scheduled an account add or remove by checking the file
        added_or_removed_account = os.path.exists(ADD_REMOVE_USER_PATH)
        # Disable buttons if we already scheduled
        if added_or_removed_account:
            self.disable_buttons()

        self.pack_start(main_heading.container, False, False, 0)
        self.pack_start(self.pass_button.align, False, False, 0)
        self.pack_start(accounts_heading.container, False, False, 0)
        self.pack_start(button_align, False, False, 0)

        self.win.show_all()

    def go_to_password_screen(self, widget, event):
        self.win.clear_win()
        SetPassword(self.win)

    # Gets executed when ADD button is clicked
    def add_account(self, widget=None, event=None):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            # Bring in message dialog box
            dialog_title = self.data["ADD_ACCOUNT_DIALOG_TITLE"]
            dialog_description = self.data["ADD_ACCOUNT_DIALOG_DESCRIPTION"]

            kdialog = kano_dialog.KanoDialog(
                dialog_title,
                dialog_description,
                parent_window=self.win
            )
            kdialog.run()
            # add new user command
            os.system("kano-init newuser")
            self.disable_buttons()

    # Gets executed when REMOVE button is clicked
    def remove_account_dialog(self, widget=None, event=None):

        if not hasattr(event, 'keyval') or event.keyval == 65293:
            dialog_title = self.data["REMOVE_ACCOUNT_DIALOG_TITLE"]
            dialog_description = self.data["REMOVE_ACCOUNT_DIALOG_DESCRIPTION"]
            # Bring in message dialog box
            kdialog = kano_dialog.KanoDialog(
                dialog_title,
                dialog_description,
                {
                    "OK": {
                        "return_value": -1
                    },
                    "CANCEL": {
                        "return_value": 0
                    }
                },
                parent_window=self.win
            )
            response = kdialog.run()
            if response == -1:

                # remove current user command
                os.system('kano-init deleteuser %s' % (get_user_unsudoed()))
                self.disable_buttons()

                # back up profile
                if has_token():
                    os.system("kano-sync --sync --backup")

                kdialog = kano_dialog.KanoDialog(
                    "To finish removing this account, you need to reboot",
                    "Do you want to reboot?",
                    {
                        "YES": {
                            "return_value": -1
                        },
                        "NO": {
                            "return_value": 0,
                            "color": "red"
                        }
                    },
                    parent_window=self.win
                )
                response = kdialog.run()
                if response == -1:
                    os.system("sudo reboot")

    # Disables both buttons and makes the temp 'flag' folder
    def disable_buttons(self):

        self.add_button.set_sensitive(False)
        self.remove_button.set_sensitive(False)
        self.added_or_removed_account = True

        ensure_dir(ADD_REMOVE_USER_PATH)


class SetPassword(Template):
    data = get_data("SET_PASSWORD")

    def __init__(self, win):
        main_title = self.data["LABEL_1"]
        main_description = self.data["LABEL_2"]
        entry_heading_1 = self.data["ENTRY_HEADING_1"]
        entry_heading_2 = self.data["ENTRY_HEADING_2"]
        entry_heading_3 = self.data["ENTRY_HEADING_3"]
        description_1 = self.data["DESCRIPTION_1"]
        description_2 = self.data["DESCRIPTION_2"]
        description_3 = self.data["DESCRIPTION_3"]

        kano_text = self.data["KANO_BUTTON"]
        Template.__init__(self, main_title, main_description, kano_text)

        self.labelled_entries = LabelledEntries(
            [{"heading": entry_heading_1, "subheading": description_1},
             {"heading": entry_heading_2, "subheading": description_2},
             {"heading": entry_heading_3, "subheading": description_3}]
        )

        self.entry1 = self.labelled_entries.get_entry(0)
        self.entry1.set_size_request(300, 44)
        self.entry1.set_visibility(False)
        self.entry1.props.placeholder_text = entry_heading_1

        self.entry2 = self.labelled_entries.get_entry(1)
        self.entry2.set_size_request(300, 44)
        self.entry2.set_visibility(False)
        self.entry2.props.placeholder_text = entry_heading_2

        self.entry3 = self.labelled_entries.get_entry(2)
        self.entry3.set_size_request(300, 44)
        self.entry3.set_visibility(False)
        self.entry3.props.placeholder_text = entry_heading_3

        self.entry1.connect("key_release_event", self.enable_button)
        self.entry2.connect("key_release_event", self.enable_button)
        self.entry3.connect("key_release_event", self.enable_button)

        self.win = win
        self.win.set_main_widget(self)

        self.box.pack_start(self.labelled_entries, False, False, 0)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.go_to_accounts)

        self.kano_button.set_sensitive(False)
        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)

        self.win.show_all()

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:

            # This is a callback called by the main loop, so it's safe to
            # manipulate GTK objects:
            watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
            self.win.get_window().set_cursor(watch_cursor)
            self.kano_button.set_sensitive(False)

            def lengthy_process():

                old_password = self.entry1.get_text()
                new_password1 = self.entry2.get_text()
                new_password2 = self.entry3.get_text()

                # Verify the current password in the first text box
                # Get current username
                username, e, num = utils.run_cmd("echo $SUDO_USER")

                # Remove trailing newline character
                username = username.rstrip()

                if not pam.authenticate(username, old_password):
                    title = "Could not change password"
                    description = "Your old password is incorrect!"

                # If the two new passwords match
                elif new_password1 == new_password2:
                    out, e, cmdvalue = utils.run_cmd("echo $SUDO_USER:%s | chpasswd" % (new_password1))

                    # if password is not changed
                    if cmdvalue != 0:
                        title = self.data["PASSWORD_ERROR_TITLE"]
                        description = self.data["PASSWORD_ERROR_1"]
                    else:
                        title = self.data["PASSWORD_SUCCESS_TITLE"]
                        description = self.data["PASSWORD_SUCCESS_DESCRIPTION"]
                else:
                    title = self.data["PASSWORD_ERROR_TITLE"]
                    description = self.data["PASSWORD_ERROR_2"]

                def done(title, description):
                    response = create_dialog(title, description, self.win)

                    self.win.get_window().set_cursor(None)
                    self.kano_button.set_sensitive(True)

                    self.clear_text()

                    if response == 0:
                        self.go_to_accounts()

                GObject.idle_add(done, title, description)

            thread = threading.Thread(target=lengthy_process)
            thread.start()

    def go_to_accounts(self, widget=None, event=None):
        self.win.clear_win()
        SetAccount(self.win)

    def clear_text(self):
        self.entry1.set_text("")
        self.entry2.set_text("")
        self.entry3.set_text("")

    def enable_button(self, widget, event):
        text1 = self.entry1.get_text()
        text2 = self.entry2.get_text()
        text3 = self.entry3.get_text()
        self.kano_button.set_sensitive(text1 != "" and text2 != "" and text3 != "")


def create_dialog(message1="Could not change password", message2="", win=None):
    kdialog = kano_dialog.KanoDialog(message1, message2,
                                     {"TRY AGAIN": {"return_value": -1}, "GO BACK": {"return_value": 0, "color": "red"}},
                                     parent_window=win)
    response = kdialog.run()
    return response