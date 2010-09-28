# -*- coding: utf8 -*-
#  Pointer Focus plugin for Gedit
#
#  Copyright (C) 2010 Derek Veit
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Pointer Focus plugin package

2010-09-28
Version 1.0.0

Description:
Set the keyboard focus based on the pointer location.

Typical location:
~/.gnome2/gedit/plugins     (for one user)
    or
/usr/lib/gedit-2/plugins    (for all users)

Files:
pointerfocus.gedit-plugin   -- Gedit reads this to know about the plugin.
pointerfocus/               -- Package directory
    __init__.py             -- Package module loaded by Gedit.
    pointer_focus.py        -- Plugin and plugin helper classes.
    gpl.txt                 -- GNU General Public License.

"""
from .pointer_focus import PointerFocusPlugin

