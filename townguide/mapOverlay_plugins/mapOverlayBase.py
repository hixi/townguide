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


class mapOverlayBase():
    """
    The base townguide mapOverlay renderer class.
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
        Intialise the gridOverlay renderer.  Does not do anything - to draw
        the grid you need to call the 'render()' method.
        """
        print "gridOverlay.__init__"
        self.townguide = townguide

        self.townguide.preferences.applyDefaults(self.defPrefs)
        self.fntSize = int(self.townguide.preferences_list['labelsize']) \
            * int(self.townguide.preferences_list['dpi'])/72


    def loadImage(self,fname):
        print "loadImage()"
        self.fname = fname
        self.im = Image.open(self.fname)
        self.draw = ImageDraw.Draw(self.im)

    def initialiseAgg(self):
        print "initialiseAgg()"
        # AGG MARKERS
        self.agg_canvas = aggdraw.Draw(self.im)
        self.agg_pen  = aggdraw.Pen("black", 4)
        
        self.agg_grid_lines_pen = aggdraw.Pen("#dddddd", 3, opacity=70)
        
        # This should change on the fly according to the marker
        self.agg_brush = aggdraw.Brush("#d11233", opacity=200)
        
        
        self.fntSize = int(self.townguide.preferences_list['labelsize']) * \
            int(self.townguide.preferences_list['dpi'])/72
        
        # AGG font import
        self.agg_font_grid_labels = aggdraw.Font("black", 
                                            self.townguide.fntPath, 
                                            self.fntSize*1, 
                                            opacity=255) # units
        self.agg_font_big = aggdraw.Font("black", 
                                    self.townguide.fntPath, 
                                    self.fntSize*3, 
                                    opacity=255) # units
        self.agg_font_medium = aggdraw.Font("black", 
                                       self.townguide.fntPath, 
                                       self.fntSize*1.3, 
                                       opacity=255) # tens
        self.agg_font_small = aggdraw.Font("black", 
                                      self.townguide.fntPath, 
                                      self.fntSize*0.8, 
                                      opacity=255) # tens
        
        self.agg_font_clusters = aggdraw.Font("white", 
                                         self.townguide.fntPath, 
                                         self.fntSize*1.3, 
                                         opacity=255)


    def saveImage(self):
        print "saveImage()"
        del self.draw

        f = open(self.fname,'w')
        self.agg_canvas.flush()
        self.im.save(f,"PNG")
        f.close()

    def renderBody(self):
        print "renderBody()"
        print "YOU HAVE MADE A MISTAKE - YOU SHOULD HAVE RE-DEFINED renderBody()"
        print "*************************************************************"

    def render(self,fname):
        """
        Draw the grid onto the specified image file.
        """
        self.loadImage(fname)
        self.initialiseAgg()
        self.renderBody()
        self.saveImage()


