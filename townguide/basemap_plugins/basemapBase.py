#!/usr/bin/python
#
#    This file is part of townguide - a simple utility to produce a
#    town guide identifying key amenities from OpenStreetMap data.
#
#    Townguide is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Townguide is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with townguide.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright Graham Jones 2010
#

import os


class basemapBase():
    """
    The base basemap map render class.
    It does not do anything, so must be subclassed to define the render()
    method, but this deals with the housekeeping and interface to townguide.

    """

    """
    Re-Define self.defPrefs to set default preferences for the parameters
    that are used by the renderer class, in cse they are not specified
    by the user in the configuration file.
    """
    defPrefs = {
        'dpi':'100',
        'datadir':'.',
        'labelsize':'12'
        }

    
    
    def __init__(self, townguide):
        """
        Intialise the basemap renderer.  Does not do anything - to draw
        the map you need to call the 'render()' method.
        """
        print "basemapBase.__init__"
        self.townguide = townguide

        self.townguide.preferences.applyDefaults(self.defPrefs)

        try:
            import mapnik2 as mapnik
            self.HAS_MAPNIK2 = True
        except:
            import mapnik
            self.HAS_MAPNIK2 = False


    def loadMapnikXML(self):
        pass

    def modifyMapnikStyle(self):
        pass

    def renderImage(fname):
        pass


    def render(self,fname):
        """
        Draw the map onto the specified image file.
        """
        self.loadMapnikXML()
        self.modifyMapnikStyle()
        self.renderImage(fname)


