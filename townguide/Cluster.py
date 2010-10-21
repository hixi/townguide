#!/usr/bin/env python
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
#    Copyright Waldemar Quevedo (GSoC 2010)
#
#
#

from math import sqrt

class Cluster:
    """
    Class to support the cluster markers feature.
    Usage: Cluster('feature')
    centroid (lat, lon)
    pois: List of pois.
    feature: string that identifies this cluster type of POI
    """ 
    
    def add_poi(self, poi):
        """ Should add a poi to the list and
        and recalculate the centroid of the cluster
        """
        self.pois.append(poi)
        self.calculate_centroid()
        
    def calculate_centroid(self):
        """ Given a list of pois, it will calculate the centroid
        of the current cluster.
        """
        sumx = 0                        # lon
        sumy = 0                        # lat
        
        for poi in self.pois:
            cx = poi[7]                 # lon
            cy = poi[6]                 # lat
            sumx += cx
            sumy += cy

        centroid_x = float(sumx / len(self.pois))
        centroid_y = float(sumy / len(self.pois))
        self.centroid = (centroid_y, centroid_x)
        return self.centroid
    
    def total_pois(self):
        """ Counts how many POIs are there in the lists
        """
        return len(self.pois)

    def is_empty(self):
        if len(self.pois) > 0:
            return False
        else:
            return True

    def distance_from_poi(self,poi):
        print "with POI:", poi
        print "calculating distance from:(x,y)", self.centroid[1], self.centroid[0], " to: ", poi[7], poi[6]        
        return sqrt((poi[6] - self.centroid[0]) ** 2 + (poi[7] - self.centroid[1]) ** 2)

    def __str__(self):
        return "<Cluster %s Lat: %f | Lon: %f> " % (self.feature, self.centroid[1], self.centroid[0])

    def __init__(self, feature):
        self.pois = []
        self.centroid = (0,0)                    # lat, lon
        self.feature = feature
        
        
