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
Version history:
2010-09-28  Version 1.0.0
    Initial release

Classes:
PointerFocusPlugin          -- object is loaded once by an instance of Gedit
PointerFocusWindowHelper    -- object is constructed for each Gedit window

"""

import gedit
import gtk

from .logger import Logger
LOGGER = Logger(level=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')[2])

class PointerFocusPlugin(gedit.Plugin):
    
    """
    An object of this class is loaded once by a Gedit instance.
    
    It creates a PointerFocusWindowHelper object for each Gedit main window.
    
    Public methods:
    activate        -- Gedit calls this to start the plugin.
    deactivate      -- Gedit calls this to stop the plugin.
    
    """
    
    def __init__(self):
        """Initialize plugin attributes."""
        LOGGER.log()
        
        gedit.Plugin.__init__(self)
        
        self._instances = {}
        """Each Gedit window will get a PointerFocusWindowHelper instance."""
    
    def activate(self, window):
        """Start a PointerFocusWindowHelper instance for this Gedit window."""
        LOGGER.log()
        if not self._instances:
            LOGGER.log('Pointer Focus activating.')
        self._instances[window] = PointerFocusWindowHelper(window)
        self._instances[window].activate()
    
    def deactivate(self, window):
        """End the PointerFocusWindowHelper instance for this Gedit window."""
        LOGGER.log()
        self._instances[window].deactivate()
        self._instances.pop(window)
        if not self._instances:
            LOGGER.log('Pointer Focus deactivated.')

class PointerFocusWindowHelper(object):
    
    """
    PointerFocusPlugin creates a PointerFocusWindowHelper object for each Gedit
    window.
    
    Public methods:
    activate    -- PointerFocusPlugin calls this when Gedit calls activate for
                   this window.
    deactivate  -- PointerFocusPlugin calls this when Gedit calls deactivate for
                   this window.
    
    """
    
    def __init__(self, window):
        """Initialize attributes for this window."""
        LOGGER.log()
        
        self._window = window
        """The window this PointerFocusWindowHelper runs on."""
        
        self._handlers_per_notebook = {}
        """A signal handler for each gtk.Notebook."""
    
        self._handlers_per_focusable = {}
        """A signal handler for each focusable widget."""
    
    def activate(self):
        """Start this instance of Pointer Focus."""
        LOGGER.log()
        LOGGER.log('Pointer Focus activating for %s' % self._window)
        
        notebooks = self._get_notebooks(self._window)
        LOGGER.log('notebooks:\n %s' %
                   '\n '.join([repr(x) for x in notebooks]))
        self._connect_notebooks(notebooks)
        
        focusables = set()
        for notebook in notebooks:
            focusables |= self._get_focusables(notebook)
        LOGGER.log('focusables:\n %s' %
                   '\n '.join([repr(x) for x in focusables]))
        self._connect_focusables(focusables)
    
    def deactivate(self):
        """End this instance of Pointer Focus."""
        LOGGER.log()
        self._disconnect_notebooks()
        self._disconnect_focusables()
        LOGGER.log('Pointer Focus deactivated for %s' % self._window)
    
    # Collect widgets
    
    def _get_notebooks(self, widget, original=True):
        """Return a set of gtk.Notebook widgets."""
        if original:
            LOGGER.log()
        notebooks = set()
        
        try:
            children = widget.get_children()
        except AttributeError:
            pass
        else:
            if isinstance(widget, gtk.Notebook):
                notebooks.add(widget)
            for child in children:
                notebooks |= self._get_notebooks(child, False)
        return notebooks
    
    def _get_focusables(self, widget, original=True):
        """Return a set of widgets that can grab focus."""
        if original:
            LOGGER.log()
        focusables = set()
        
        can_focus = widget.get_property('can_focus')
        if can_focus:
            focusables.add(widget)
        try:
            children = widget.get_children()
        except AttributeError:
            pass
        else:
            for child in children:
                focusables |= self._get_focusables(child, False)
        return focusables
    
    # Respond to a notebook page added
    # (e.g. if a document is opened or a paned plugin is activated).
    
    def _connect_notebooks(self, notebooks):
        """Connect to the 'add' signal of each gtk.Notebook widget."""
        LOGGER.log()
        for notebook in notebooks:
            self._handlers_per_notebook[notebook] = notebook.connect(
                'page-added', self._on_page_added)
            LOGGER.log('Connected to %r' % notebook)
    
    def _disconnect_notebooks(self):
        """Disconnect signal handlers from gtk.Notebook widgets."""
        LOGGER.log()
        for notebook in self._handlers_per_notebook:
            notebook.disconnect(self._handlers_per_notebook[notebook])
            LOGGER.log('Disconnected from %r' % notebook)
        self._handlers_per_notebook = {}
    
    def _on_page_added(self, notebook, child, page_num):
        """Connect signal handlers to widgets within the new page."""
        LOGGER.log()
        LOGGER.log('%r has new page [%d] %r' % (notebook, page_num, child))
        focusables = self._get_focusables(child)
        self._connect_focusables(focusables)
    
    # Respond to the pointer entering a focusable widget.
    
    def _connect_focusables(self, focusables):
        """Connect to the 'enter-notify-event' signal of each widget."""
        LOGGER.log()
        for focusable in focusables:
            focusable.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
            self._handlers_per_focusable[focusable] = focusable.connect(
                'enter-notify-event', self._on_enter_notify_event)
            LOGGER.log('Connected to %r' % focusable)
    
    def _disconnect_focusables(self):
        """Disconnect signal handlers from focusable widgets."""
        LOGGER.log()
        for focusable in self._handlers_per_focusable:
            focusable.disconnect(self._handlers_per_focusable[focusable])
            LOGGER.log('Disconnected from %r' % focusable)
        self._handlers_per_focusable = {}
    
    def _on_enter_notify_event(self, widget, event):
        """Have the widget grab the keyboard focus."""
        LOGGER.log()
        LOGGER.log('The pointer entered %r at (%d, %d)' %
                   (widget, event.x, event.y))
        widget.grab_focus()

