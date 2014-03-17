#!/usr/bin/env python

# fixed-size-box
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Ceates a fixed size box, which we use across the levels for consistancy.

from gi.repository import Gtk


class Fixed(Gtk.Box):

    def __init__(self):
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.set_size_request(400, 125)
        #self.box.props.valign = Gtk.Align.CENTER
        #self.box.props.halign = Gtk.Align.CENTER
