#!/usr/bin/env python

# config_file.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functions controlling reading and writing to config file
#

import os
import re
from kano.utils import ensure_dir, get_user_unsudoed, read_json, write_json

USER = None
USER_ID = None

username = get_user_unsudoed()
settings_dir = os.path.join('/home', username, '.kano-settings')
if os.path.exists(settings_dir) and os.path.isfile(settings_dir):
    os.rename(settings_dir, settings_dir + '.bak')
ensure_dir(settings_dir)
settings_file = os.path.join(settings_dir, 'config')

defaults = {
    'Email': '',
    'Keyboard-continent-index': 1,
    'Keyboard-country-index': 21,
    'Keyboard-variant-index': 0,
    'Keyboard-continent-human': 'america',
    'Keyboard-country-human': 'United States',
    'Keyboard-variant-human': 'Generic',
    'Audio': 'Analogue',
    'Wifi': '',
    'Display-mode': 'auto',
    'Display-mode-index': 0,
    'Display-overscan': 0,
    'Overclocking': 'High',
    'Mouse': 'Normal',
    'Wallpaper': 'kanux-background'
}


def replace(fname, pat, s_after):
    # See if the pattern is even in the file.
    with open(fname) as f:
        pat = re.escape(pat)
        if not any(re.search(pat, line) for line in f):
            return  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()
        os.rename(out_fname, fname)


def get_setting(variable):
    data = read_json(settings_file)
    if variable not in data:
        if variable not in defaults:
            print 'Defaults not found for variable: {}'.format(variable)
        return defaults[variable]
    return data[variable]


def set_setting(variable, value):
    data = read_json(settings_file)
    data[variable] = value
    write_json(settings_file, data)

    # TODO chown to user


