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

class poiOverlay(mapOverlayBase.mapOverlayBase):
    """
    A townguide mapOverlay renderer that draws numbered markers to show points
    of interest on the map image.

    It uses the following parameters in townguide.preferences.list:


    """
    
    def renderBody(self):
        """
        Draw the pois onto the specified image file.
        """
        print "poiOverlay.render()"

        featurelist = self.townguide.amenities.keys()
        featurelist.sort()
        featureNo = 1
        for feature in featurelist:
            for rec in self.townguide.amenities[feature]:
                # (1, 1, (684200276, None, None, None, 'convenience', None, 7303119.8913879804, -131831.99940327799))
                print featureNo, rec
                if len(rec[2])==8:
                    fx = rec[2][7]
                    fy = rec[2][6]
                else:
                    print "****ERROR - No Location for record ",rec,"*****"
                    print "This is probably because this PoI is an area, not a node"
                    print "I will fix this eventually!!!"
                    fx = self.townguide.c0.x
                    fy = self.townguide.c0.y
                imx = int((fx - self.townguide.c0.x)
                          / self.townguide.preferences_list['oscale'])
                imy = self.im.size[1] - int((fy - self.townguide.c0.y) / 
                                       self.townguide.preferences_list['oscale'])
                # print "fx=%d imx=%d c0.x=%d, fy=%d imy=%d c0.y=%d, scale=%f" %\
                    #      (fx,imx,self.c0.x,fy,imy,self.c0.y, scale)
                markerSize = int(self.townguide.preferences_list['markersize'])*\
                    int(self.townguide.preferences_list['dpi'])/72

                origin_x = imx - markerSize/2
                origin_y = imy - markerSize/2

                # Agg markers
                self.agg_canvas.polygon((origin_x, origin_y,
                                    origin_x - 2 * markerSize, origin_y - 4 * markerSize,
                                    origin_x, origin_y - 6 * markerSize,
                                    origin_x + 2 * markerSize, origin_y - 4 * markerSize),
                                   self.agg_pen, self.agg_brush)
                    
                # If the number of the marker is a unit, it will appear in a bigger size
#                if featureNo < 10:
#                    self.agg_canvas.text((origin_x - 0.9*markerSize,
#                                     origin_y - 5.4*markerSize),
#                                    "%d" % featureNo,
#                                    self.agg_font_big)
#                elif featureNo >= 10 or featureNo < 100:
                self.agg_canvas.text((origin_x - 0.9*markerSize,
                                      origin_y - 4.0*markerSize),
                                     "%d" % featureNo,
                                     self.agg_font_medium)
#                elif featureNo >= 100:
#                    self.agg_canvas.text((origin_x - 0.9*markerSize,
#                                     origin_y - 5.4*markerSize),
#                                    "%d" % featureNo,
#                                    self.agg_font_small)
                featureNo += 1

                    
