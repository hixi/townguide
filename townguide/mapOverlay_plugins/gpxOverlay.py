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
import Image, ImageDraw, ImageFont
import aggdraw
from townguide.utils import is_true
import mapOverlayBase
import mapnik2 as mapnik

class gpxOverlay(mapOverlayBase.mapOverlayBase):
    """
    A townguide mapOverlay renderer that draws gpx tracks and waypoints over 
    a base map.

    It uses the following parameters in townguide.preferences.list:
    gpxTrack:  true/false
    gpxTrackFile:  <path to file containing gpx track points>
    gpxWaypts:  true/false
    gpxWayptsFile:  <path to file containing gpx waypoints

    """
    def renderBody(self):
        """
        Draw the GPX Track onto the specified image file.
        """
        print "gpxOverlay.render()"

        #####################################################
        # Now add the gpx Track
        if is_true(self.townguide.preferences_list['gpxTrack']):
            print "Adding gpx tracks."
            s = mapnik.Style()
            r = mapnik.Rule()
            r.symbols.append(mapnik.RasterSymbolizer())
            s.rules.append(r)



        else:
            print "gpxTrack is False - not plotting track"

        if is_true(self.townguide.preferences_list['gpxWaypts']):
            print "Adding gpx waypoints."
        else:
            print "gpxWaypts is False - not plotting waypoints"



