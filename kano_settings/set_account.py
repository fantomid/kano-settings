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

from kano.utils import get_user_unsudoed, ensure_dir
from kano_settings.templates import TopBarTemplate, Template
import kano.utils as utils
import pam


ADD_REMOVE_USER_PATH = '/tmp/kano-init/add-remove'


class SetAccount(TopBarTemplate):
    def __init__(self, win):
        TopBarTemplate.__init__(self)

        self.win = win
        self.win.set_main_widget(self)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        self.added_or_removed_account = False

        main_heading = Heading("System account settings", "Set your account")

        self.pass_button = KanoButton("CHANGE PASSWORD")
        self.pass_button.pack_and_align()
        self.pass_button.connect("button-release-event", self.go_to_password_screen)

        self.add_button = KanoButton("ADD ACCOUNT")
        self.add_button.set_size_request(200, 44)
        self.add_button.connect("button-release-event", self.add_account)

        self.remove_button = KanoButton("REMOVE ACCOUNT", color="red")
        self.remove_button.set_size_request(200, 44)
        self.remove_button.connect("button-release-event", self.remove_account_dialog)

        button_container = Gtk.Box()
        button_container.pack_start(self.add_button, False, False, 10)
        button_container.pack_start(self.remove_button, False, False, 10)

        button_align = Gtk.Alignment(xscale=0, xalign=0.5)
        button_align.add(button_container)

        accounts_heading = Heading("Accounts", "Add or remove accounts")

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
            kdialog = kano_dialog.KanoDialog("New account scheduled.",
                                             "Reboot the system.",
                                             parent_window=self.win)
            kdialog.run()
            # add new user command
            os.system("kano-init newuser")
            self.disable_buttons()

    # Gets executed when REMOVE button is clicked
    def remove_account_dialog(self, widget=None, event=None):

        if not hasattr(event, 'keyval') or event.keyval == 65293:
            # Bring in message dialog box
            kdialog = kano_dialog.KanoDialog(
                "Are you sure you want to delete the current user?",
                "",
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

    # Disables both buttons and makes the temp 'flag' folder
    def disable_buttons(self):

        self.add_button.set_sensitive(False)
        self.remove_button.set_sensitive(False)
        self.added_or_removed_account = True

        ensure_dir(ADD_REMOVE_USER_PATH)


class SetPassword(Template):
    def __init__(self, win):
        Template.__init__(self, "Change your password", "Keep out the baddies!", "APPLY CHANGES")

        self.labelled_entries = LabelledEntries([{"heading": "Old password", "subheading": '"Kano" is default'},
                                                {"heading": "New password", "subheading": ""},
                                                {"heading": "Repeat new password", "subheading": ""}])

        self.entry1 = self.labelled_entries.get_entry(0)
        self.entry1.set_size_request(300, 44)
        self.entry1.set_visibility(False)
        self.entry1.props.placeholder_text = "Old password"

        self.entry2 = self.labelled_entries.get_entry(1)
        self.entry2.set_size_request(300, 44)
        self.entry2.set_visibility(False)
        self.entry2.props.placeholder_text = "New password"

        self.entry3 = self.labelled_entries.get_entry(2)
        self.entry3.set_size_request(300, 44)
        self.entry3.set_visibility(False)
        self.entry3.props.placeholder_text = "Repeat new password"

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

        self.win.show_all()

    def apply_changes(self, button, event):

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
                    title = "Could not change password"
                    description = "Your new password is not long enough or contains special characters."
                else:
                    title = "Password changed!"
                    description = ""
            else:
                title = "Could not change password"
                description = "Your new passwords don't match!  Try again"

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
