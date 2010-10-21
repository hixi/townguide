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
import mapOverlayBase

class gridOverlay(mapOverlayBase.mapOverlayBase):
    """
    A townguide mapOverlay renderer that draws a grid at a specified spacing
    on the map image.

    It uses the following parameters in townguide.preferences.list:


    """
    
#    def __init__(self, townguide):
#        """
#        Intialise the gridOverlay renderer.  Does not do anything - to draw
#        the grid you need to call the 'render()' method.
#        """
#        print "gridOverlay.__init__"
#        self.townguide = townguide
#
#        defPrefs = {
#            'dpi':'100',
#            'datadir':'.',
#            'labelsize':'12'
#            }
#
#        self.townguide.preferences.applyDefaults(defPrefs)
        

    def renderBody(self):
        """
        Draw the grid onto the specified image file.
        """
        print "gridOverlay.renderBody()"

        #####################################################
        # Now add the grid and labels
        print "Adding grid and labels to the map..."

        print "Drawing grid on page."
        labels_size = 12
            
        for x in range(0,self.townguide.map_size_x):
                
            # vertical grid line
            xpx = x * self.townguide.preferences_list['tilesize'] / self.townguide.preferences_list['oscale']
                
            self.agg_canvas.line((xpx,0,xpx,self.im.size[1]), self.agg_grid_lines_pen)

            # Get label letter
            str = self.townguide.xLabel(x)
            self.agg_canvas.text((xpx+self.townguide.preferences_list['tilesize'] / self.townguide.preferences_list['oscale']/2,1),                             
                            str,
                            self.agg_font_grid_labels)
            # Labels that appear below in the map
            self.agg_canvas.text(
                (xpx+self.townguide.preferences_list['tilesize']
                 / self.townguide.preferences_list['oscale']/2, 
                 self.im.size[1] - 1 * self.fntSize),                    
                str,
                self.agg_font_grid_labels)

        for y in range(0,self.townguide.map_size_y):
            # horizontal grid line
            ypx = (self.townguide.map_size_y-y-1)*self.townguide.preferences_list['tilesize']/self.townguide.preferences_list['oscale']
                        
            self.agg_canvas.line((0,ypx,self.im.size[0],ypx), self.agg_grid_lines_pen)
            
            str = self.townguide.yLabel(y)
            self.agg_canvas.text(
                (1,
                 ypx+self.townguide.preferences_list['tilesize']
                 / self.townguide.preferences_list['oscale']/2),                
                            str,
                            self.agg_font_grid_labels)
            self.agg_canvas.text(
                (self.im.size[0]- 2 * self.fntSize, 
                 ypx + self.townguide.preferences_list['tilesize']
                 / self.townguide.preferences_list['oscale']/2),     
                            str,
                            self.agg_font_grid_labels)


