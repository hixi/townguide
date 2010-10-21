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
#    Copyright Graham Jones 2009
#
#
#

"""
A program to produce a printable guide to a specified region uisng OpenStreetMap Data.

Summary
=======
Townguide is a simple utility to produce a printable guide to
an area (a 'town') from OpenStreetMap data (http://www.openstreetmap.org).
The data to be used must first have been imported into a postgresql
database using the osm2pgsql utility
(see http://wiki.openstreetmap.org/mapnik).

Dependencies
============
It also needs a working copy of the mapnik map rendering library with
python bindings.
The safest thing to do to make sure it works is to follow the instructions
on the OpenStreetMap Wiki for rendering maps using mapnik - once that works
townguide should work ok.
Some of the dependencies are:
1. psycopg interface to link python to postgresql.
2. mapnik (http://www.mapnik.org)
3. Python Imaging Library (PIL).
4. prefs.py and prefs.glade - simple library to parse the configurationfile. Provided with townguide source.

Configuration File
==================
Townguide takes an XML configuration file as its input.
The structure is a simple list of named elements with values
such as <title>This is the Title</title>.
The following elements should be present.  Note that there is currently
no error checking on this - if a required element is missing townguide
will crash with an obscure error!

origin - (float(lat) , float(lon))the lattitude and longitude (lat,lon) of the bottom left corner of the
region to be analysed.

tilesize - (float(size))the size in meters of the grid tiles to divide the area into (1000=1km)

mapsize - (int(map_size_x), int(map_size_y) - the size of the region in number of tiles in the x and y direction.

oscale (float(oscale)) - the scale of the main overview map in metres per pixel.

features (string) - a comma separated list of the features to be listed in the features page.  The list should be [column]=[value] pairs that are valid to use
in a SQL staatement on the osm2pgsql generated database.  This means that for string queries, the value should be included in single quotes.  See the example file hartlepool.xml for info.

title (string) - the title to be used for the guide in the rendered output.

format (string) - the format of the rendered output to be produced.  The only valid value at the moment is 'html' - the intention is that the default will be pdf eventually.

outdir (string) - the directory to be used for output - this must not exist or the program exits with an error.

debug (string) - True or False to switch debugging information on and off.

Note that all columns specified in this file must have been selected in the
default.style file used to import the database using osm2pgsql.  The default
file that comes with osm2pgsql does not include the shop column, so this needs
adding for the following example to work.

A valid example is shown below:
<xml>
  <origin>54.68376,-1.21583</origin>
  <mapsize>3,3</mapsize>
  <detailsize>5</detailsize>
  <tilesize>1000</tilesize>
  <oscale>10</oscale>
  <features>
    amenity='bank',
    shop='supermarket',
    highway='residential',
  </features>
  <title>Hartlepool Free Street Map</title>
  <format>html</format>
  <outdir>hartlepool</outdir>
<debug>False</debug>
</xml>

$LastChangedDate: 2010-04-25 13:41:20 -0500 (, 25  4 2010) $
$Rev: 73 $
$Author: grahamjones139 $
"""

import sys
import psycopg2 as psycopg

try:
    import mapnik2 as mapnik
    HAS_MAPNIK2 = True
except:
    import mapnik
    HAS_MAPNIK2 = False

import Image, ImageDraw, ImageFont
import aggdraw        
import os
import string

# Townguide utils
from prefs import prefs
from utils import is_true

# Experimental Cluster Markers
from Cluster import Cluster

# Import the needed plugins...
# FIXME: Plugins should not be explicitly included here
# FIXME: something like `import plugins`, would be better
from plugins.posterRenderer       import posterRenderer
from plugins.newPosterRenderer    import newPosterRenderer
from plugins.htmlRenderer         import htmlRenderer
from plugins.bookRenderer         import bookRenderer
# Plugin support: change 1
from plugins.simpleLandscapeRenderer      import simpleLandscapeRenderer
from plugins.simplePosterRenderer         import simplePosterRenderer

from mapOverlay_plugins import gridOverlay
from mapOverlay_plugins import poiOverlay
from mapOverlay_plugins import clusterOverlay
from mapOverlay_plugins import gpxOverlay


import defaults

class townguide:
    """
    The main townguide program is stored in the townguide class.
    As written this is pretty pointless, but I think I will need this
    when I implement output plugins to do rendering and want to pass
    all of the data to the plugin.
    
    """
    def __init__(self, preferences):
        """Initialise the townguide generating class from the set of
        preferences specified in the dictionary 'preferences_list'.   The required data
        is then extracted from the database, and the selected output renderer
        called.
        """
        defaults_options = defaults.DEFAULT_PREFERENCES
        self.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over"

        self.preferences = preferences
        self.preferences_list = preferences.getPrefs()

        print 'PREFERENCES_LIST!!!'
        print self.preferences_list
        
        self.preferences.applyDefaults(defaults_options)
        self.preferences_list = preferences.getPrefs()
        # print "datadir=%s" % self.preferences_list['datadir']
        
        if is_true(self.preferences_list['debug']):
            self.debug = True
        else:
            self.debug = False

        # FIXME: import the fonts that are distributed with townguide.
        # if the font exists inside the data dir
        # fntPath = "%s/FreeSerif.ttf" % self.preferences_list['datadir']
        if os.path.isfile(self.preferences_list['datadir']):
            print 'Custom font exists! Using that instead'
        else:
            # Use the FreeSerif font that is bundled with townguide
            print "Could not find custom font!!!"
            print "Using the bundled font from Townguide"
            pk_path, filename =  os.path.split(os.path.abspath(__file__))
            self.fntPath = os.path.join(pk_path, 'fonts', 'DroidSans.ttf')
            print "font located at: ", self.fntPath
        
        print "fntPath = %s." % self.fntPath



        # Getting lat and long
        (lat,lon) = self.preferences_list['origin'].split(',')
        
        lat = float(lat)
        lon = float(lon)

        (map_size_x,map_size_y) = self.preferences_list['mapsize'].split(',')
        map_size_x = int(map_size_x)
        map_size_y = int(map_size_y)
        self.preferences_list['map_size_x'] = map_size_x
        self.preferences_list['map_size_y'] = map_size_y
        self.preferences_list['tilesize'] = float(self.preferences_list['tilesize'])
        oscale = float(self.preferences_list['oscale'])
        self.preferences_list['oscale'] = float(self.preferences_list['oscale'])
        
        # self.features is the list of map features to be presented.
        self.features = []
        featstrs = self.preferences_list['features'].split(',')
        for feat in featstrs:
            self.features.append(str(feat.strip()))
        # if self.debug: print self.features
        # if self.debug: print "lat=%f, lon=%f, map_size_x=%d, map_size_y=%d" % (lat,lon,map_size_x,map_size_y)

        #Convert the lat/long origin into mercator projection metres.
        prj = mapnik.Projection(self.srs)
        self.c0 = prj.forward(mapnik.Coord(lon,lat))

        print "Origin (%f,%f) is equivalent to (%f,%f) in projection" %\
              (lon,lat,self.c0.x,self.c0.y)

        self.lat = lat
        self.lon = lon
        self.map_size_x = map_size_x
        self.map_size_y = map_size_y

        self.tilesize = float(self.preferences_list['tilesize'])
        self.oscale = oscale
        self.uname = self.preferences_list['uname']
        self.dbname = self.preferences_list['dbname']

        self.title = self.preferences_list['title']
        self.outdir = self.preferences_list['outdir']

        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        # ====== DOWNLOAD WITH THE XAPI ==============
        downloadStr = self.preferences_list['download']
        downloadStr = downloadStr.lower()
        if is_true(downloadStr):
            self.populateDB()
        # ============================================

        print "Extracting Map Features from Database"
        self.streetIndex = {}
        self.amenities = {}
        
        # Experimental Cluster Markers
        self.clusters = []
        
        self.amenitiesSorted = {}
        maxsize = int(self.preferences_list['maxmapsize'])
        if self.preferences_list['map_size_x'] <= int(self.preferences_list['maxmapsize']) and \
        self.preferences_list['map_size_y'] <= int(self.preferences_list['maxmapsize']):
            #FIXME:  This is wrong - we need to get the data even if we do not
            # want a street index.
            #if self.preferences_list['streetIndex'].lower() == 'true':
            self.getAmenities()
        else:
            print "Map is too big ==================================="
            print "Must be less than %d km across" % int(self.preferences_list['maxmapsize'])
            print "...but map size is %f x %f" % \
                (self.preferences_list['map_size_x'],
                 self.preferences_list['map_size_y'])
        # Supported plugins
        # Plugin support: change 2
        {'book':       self.renderBook,
         'html':       self.renderHTML,
         'poster':     self.renderPoster,
         'newposter':  self.renderNewPoster,
         'simplelandscape': self.renderSimpleLandscape,
         'simpleposter': self.renderSimplePoster,
         }[self.preferences_list['format']]()    

    def drawTile(self,tx,ty):
        minx = self.c0.x + self.preferences_list['tilesize'] * tx
        miny = self.c0.y + self.preferences_list['tilesize'] * ty
        
        if HAS_MAPNIK2:
            bbox = mapnik.Box2d(minx,
                                miny,
                                minx+self.preferences_list['tilesize'],
                                miny+self.preferences_list['tilesize'])
        else:
            bbox = mapnik.Envelope(minx,
                                   miny,
                                   minx+self.preferences_list['tilesize'],
                                   miny+self.preferences_list['tilesize'])
                
        # First draw the basic map using mapnik.
        fname = "%s/image_%02d_%02d.png" % (self.preferences_list['outdir'],tx,ty)
        
        imgx = int(self.preferences_list['tilesize']/self.preferences_list['oscale'])
        imgy = int(self.preferences_list['tilesize']/self.preferences_list['oscale'])
        self.drawTile_bbox(bbox,imgx,imgy,fname)

        return fname

    
    def drawTile_bbox(self,bbox,imgx,imgy,fname):
        """Call Mapnik to draw a map image for data in
        bounding box bbox.  The image size is imgx by imgy pixels, and
        the output filename is fname.

        29sep2009  GJ  ORIGINAL VERSION, based on generate_image.py
        06jan2010  GJ  Renamed to drawTile_bbox from drawTile
        """
        mapfile = str(self.preferences_list['mapfile'])
        map_uri = str(fname)
        print ("mapfile=%s" % mapfile)

        # png image
        m = mapnik.Map(imgx,imgy)
        mapnik.load_map(m,mapfile)
        m.zoom_to_box(bbox)
        im = mapnik.Image(imgx,imgy)

        if HAS_MAPNIK2:
            # We apply the scale factor to the map
            print 'using scale factors from mapnik2'
            scale_factor = float( self.preferences_list['dpi'] ) / 72
            print "Scale factor is: ", scale_factor, "================="
            mapnik.render(m, im, scale_factor)
        else:
            print 'NOT using scale_factors'
            mapnik.render(m, im)
            
        view = im.view(0,0,imgx,imgy) # x,y,width,height
        view.save(map_uri,'png')

        # Adding support for svg image
        #print "Creating svg image"
        #import cairo
        #svg_map_uri = ''.join([fname, ".svg"])
        #print svg_map_uri
        #svg_file = open(svg_map_uri, 'w')
        #surface = cairo.SVGSurface(svg_file.name, m.width,m.height)
        #mapnik.render(m, surface)
        #surface.finish()

        #print "Creating PDF surface image"
        #pdf_map_uri = ''.join([fname, ".pdf"])
        #print pdf_map_uri
        #pdf_file = open(pdf_map_uri, 'w')
        #surface = cairo.PDFSurface(pdf_file.name, m.width,m.height)
        #mapnik.render(m, surface)
        #surface.finish()

            
    def drawOverviewMap(self,outdir='',addFeatures=False):
        """Draws the overview map of the full area requested and
        adds a grid with row and column identifiers to the map image.
        29sep2009  GJ ORIGINAL VERSION
        01jan2010  Added option to add feature markers to map.
        17oct2010  GJ  Separated grid and features out into separate
                       overlay plugins.
        """
        # First draw the basic map using mapnik.
        fname = "%s/overview.png" % outdir

        if self.debug: print "Drawing Overview Map - fname=",fname

        c0 = self.c0

        if HAS_MAPNIK2:
            bbox = mapnik.Box2d(c0.x,
                                c0.y,
                                c0.x + self.preferences_list['tilesize'] * \
                                    self.preferences_list['map_size_x'],
                                c0.y + self.preferences_list['tilesize'] * \
                                    self.preferences_list['map_size_y'])
        else:
            bbox = mapnik.Envelope(c0.x,
                                   c0.y,
                                   c0.x + self.preferences_list['tilesize'] * \
                                       self.preferences_list['map_size_x'],
                                   c0.y + self.preferences_list['tilesize'] * \
                                       self.preferences_list['map_size_y'])
            
        # print "tilesize=%d, map_size_x=%d, oscale=%f" % (self.preferences_list['tilesize'],self.preferences_list['map_size_x'],self.preferences_list['oscale'])
        imgXpix = int(self.preferences_list['tilesize'] * 
                      self.preferences_list['map_size_x'] / 
                      self.preferences_list['oscale'])
        imgYpix = int(self.preferences_list['tilesize'] * 
                      self.preferences_list['map_size_y'] / 
                      self.preferences_list['oscale'])
        
        # print "Rendering Map to image of size (%d,%d) pixels" % (imgXpix,imgYpix)
        self.drawTile_bbox(bbox, imgXpix, imgYpix, fname)

        # FINISHED RENDERING THE IMAGE ===
        
        ###############################################################
        # Draw the grid on the map
        go = gridOverlay(self)
        go.render(fname)

        ##############################################################
        # Draw gpx Trace and waypoints on the map if requested
        overlay = gpxOverlay(self)
        overlay.render(fname)

        
        ###############################################################
        # Draw the point of interest markers on the map
        # (as long as the map is not too big).
        if self.preferences_list['map_size_x'] <= \
                int(self.preferences_list['maxmapsize']) and \
                self.preferences_list['map_size_y'] <= \
                int(self.preferences_list['maxmapsize']):
            addFeatures = True
        else:
            print "Map is too big to look for features: width: %s, height: %s" % (
                self.preferences_list['map_size_x'], self.preferences_list['map_size_y'])
            print "...but map size is %f x %f" % \
                (self.preferences_list['map_size_x'],
                 self.preferences_list['map_size_y'])

            addFeatures = False

        if addFeatures and not is_true(self.preferences_list['clusters']):
            print "Adding feature markers to map..."
            po = poiOverlay(self)
            po.render(fname)

        ###############################################################
        # Add clustered markers if requested.
        if is_true(self.preferences_list['clusters']):
            print "Adding Clusters to map ...."
            co = clusterOverlay(self)
            co.render(fname)

        # creating a thumbnail with the same image

        ##############################################################
        # Create a thumbnail image of the map.
        if is_true(self.preferences_list['withThumbnail']):
            thumbnail_name = "%s/thumbnail.png" % outdir
            thumb_im = Image.open(fname)
            # thumb_f = open(fname, 'w')        
            size = 256, 256
            thumb_im.thumbnail(size, Image.ANTIALIAS)
            thumb_im.save(thumbnail_name, "PNG")

        ##############################################################
        # End of drawOverviewMap
        ##############################################################

    def xLabel(self,x):
        """Return the appropriate text label for cell column x.
        FIXME: This will not work with more than 26 columns....
        01oct2009  GJ ORIGINAL VERSION.
        """
        labels=('A','B','C','D','E','F','G','H','I','J','K','L','M',\
                'N','O','P','Q','R','S','T','U','V','W','X','Y','Z')

        if (x<=len(labels)):
            return labels[x]
        else:
            return 'oops'
                                       

    def yLabel(self,y):
        """Return the appropriate label for cell row y."""
        return "%d" % (y+1)


    def cellLabel(self,x,y):
        """Return the appropriate text label for cell (x,y)
        """
        return "%s%s" % (self.xLabel(x), self.yLabel(y))

    def getAmenities(self):
        """Extract the required map features from the database
        for each map square and store the data in the 'amenities'
        dictionary.
        An index of the street names is stored in self.streetIndex dictionary.
        
        FIXME:  This is very inefficient - it queries the database
        for the bounding box and each required feature in turn.
        It sould be more efficient to get all of the data in the bounding
        box then query that, but I haven't done it.

        01oct2009 GJ ORIGINAL VERSION
        04oct2009  GJ Added use of expandWhereClause to allow grouping
                      of different key values under the same heading
                      in the features page.
        11oct2009 GJ  Added support for areas (polygons) as well as nodes.
        """
        # Extract the data for each 1km square.
        if (self.debug): print "getAmenities()"
        c0 = self.c0                    # lon, lat
        streetList = {}
        streetIndexSorted = {}
        print c0

        # Get all the features and then create clusters ===
        if is_true(self.preferences_list['clusters']):
            print "........... Trying out something .........."
            tilesize = self.preferences_list['tilesize']
            map_width = self.map_size_x
            map_height = self.preferences_list['map_size_y']

            min_lon = c0.x
            min_lat = c0.y
            max_lon = c0.x + (tilesize * map_width)
            max_lat = c0.y + (tilesize * map_height)

            # Experimental cluster markers
            # tolerance to become a cluster should change according to the zooming factor
            tolerance = 20 * self.map_size_x

            # k-means first iteration
            clusters = {}
            if HAS_MAPNIK2:
                bbox = mapnik.Box2d(min_lon, min_lat, max_lon, max_lat)
            else:
                bbox = mapnik.Envelope(min_lon, min_lat, max_lon, max_lat)

            for featureStr in self.features:
                title,wc = self.expandWhereClause(featureStr)
                print "::::", title, wc
                feature = title
                if self.debug: print "Extracting feature %s using %s." %\
                   (feature,featureStr)            
                pois = self.getBBContents(bbox,wc)

                # poi[6]: lat
                # poi[7]: lon
                print "Current Contents for ", featureStr, pois

                for poi in pois:
                    if not len(self.clusters) > 0:
                        print "POI:", poi
                        c = Cluster(feature)
                        c.add_poi(poi)
                        self.clusters.append(c)
                        print "Created the First cluster: ", c.centroid
                    else:
                        # Look for the custer where the POI should be inserted
                        # by noticing the difference with that cluster's centroid

                        # If the distance to that cluster's centroid is less than
                        # the tolerance it will be inserted there.                    
                        # This should work like a non-optimal first iteration of k-means
                        CLUSTER_FOUND = False
                        for (scounter, cluster) in enumerate(self.clusters):
                            distance = cluster.distance_from_poi(poi)
                            print "This cluster", cluster.pois
                            print distance
                            if distance < tolerance:
                                # Add POI to cluster
                                print "--- POI should get in this cluster"
                                cluster.add_poi(poi)
                                CLUSTER_FOUND = True
                                print "BREAK!!!"
                                break
                        if not CLUSTER_FOUND:
                            print "_____ Could not find a suited cluster _____"
                            # Create a new cluster
                            print "------ Creating a new cluster for this poi"
                            new_cluster = Cluster(feature)
                            new_cluster.add_poi(poi)
                            self.clusters.append(new_cluster)

            for kluster in self.clusters:
                print len(kluster.pois), vars(kluster)

            print "............................................."
            #=========================================================== 

        for tx in range(0,self.map_size_x):
            minx = c0.x + self.preferences_list['tilesize'] * tx
            for ty in range(0,self.preferences_list['map_size_y']):
                # sys.stdout.write("%s" % self.cellLabel(tx,ty))
                # sys.stdout.flush()
                print "%s " % self.cellLabel(tx,ty)
                miny = c0.y + self.preferences_list['tilesize'] * ty

                if HAS_MAPNIK2:
                    bbox = mapnik.Box2d(minx,
                                        miny,
                                        minx + self.preferences_list['tilesize'],
                                        miny + self.preferences_list['tilesize'])
                else:
                    bbox = mapnik.Envelope(minx,
                                           miny,
                                           minx + self.preferences_list['tilesize'],
                                           miny + self.preferences_list['tilesize'])
                
                fname = "image_%02d_%02d.png" % (tx,ty)
                #if self.debug: print bbox

                ########################################################
                # Extract points of interest into amenities dictionary #
                ########################################################
                
                for featureStr in self.features:
                    title,wc = self.expandWhereClause(featureStr)
                    # print "::::", title, wc
                    feature = title
                    if self.debug: print "Extracting feature %s using %s." %\
                       (feature,featureStr)
                    
                    # FIXME: This needs to be optimized for clustering
                    pois = self.getBBContents(bbox,wc)
                    for poi in pois:
                        if feature in self.amenities:
                            self.amenities[feature].append((tx,ty,poi))
                        else:
                            self.amenities[feature]=[(tx,ty,poi)]
                    # print self.amenities
                    # print len(self.amenities)
                    # print "__________________________________"

                ##############################################
                # Extract all of the streetnames in the cell #
                ##############################################
                bbStreets = self.getBBStreets(bbox)
                streetList[self.cellLabel(tx,ty)] = bbStreets

                # Render a high resolution tile of this cell.
                #fname = "%s/%s.png" % (self.outdir,self.cellLabel(tx,ty))
                #self.drawTile(bbox,1000,1000,fname)


        #####################################################
        # Sort the amenities list to remove duplicates      #
        # The result is self.amenitiesSorted which is a     #
        # dictionary of features.  Each feature contains    #
        # a dictionary of amenity names.   Each amenity     #
        # name entry contains a list of cell IDs as strings #
        #                                                   #
        #####################################################
        for feature in self.amenities.keys():
            # poi = (tx,ty,(id, name, operator))
            # example:
            # (0, 0, (663528594, 'Tangerine', None, 'restaurant', None, None, 4546182.5512522003, -13628929.6157306))
            for poi in self.amenities[feature]:
                cellId = self.cellLabel(poi[0],poi[1])
                osm_id = poi[2][0]      # 663528594
                name = poi[2][1]        # 'Tangerine'
                operator = poi[2][2]    # Company that runs the place
                amenityVal = poi[2][3]  # Type of amenity
                shopVal = poi[2][4]      
                landuse = poi[2][5]
                if name == None:
                    if amenityVal == None:
                        if shopVal == None:
                            if landuse == None:
                                name = "Unidentified thing - osm_id=%d" % osm_id
                            else:
                                name = "Unnamed %s" % landuse
                        else:
                            name = "Unnamed %s" % shopVal
                    else:
                        name = "Unnamed %s" % amenityVal
                        
                print "%s,  %s, %s" % (feature, name, cellId)
                # Entertainment,  Castro Theater,  A1
                if not feature in self.amenitiesSorted:
                    print "creating dictionary for feature %s" % feature
                    self.amenitiesSorted[feature]={}
                if name in self.amenitiesSorted[feature]:
                    print "dictionary %s already exists in feature %s" % (name,feature)
                    if not cellId in self.amenitiesSorted[feature][name]:
                        print "appending cellid"
                        self.amenitiesSorted[feature][name].append(cellId)
                    else:
                        print "skipping duplicate feature %s %s in %s\n" % (feature,name,cellId)
                else:
                    print "adding cell id to list"
                    self.amenitiesSorted[feature][name] = [cellId]
                    print "self.amenitiesSorted=", self.amenitiesSorted[feature][name]


        #########################################################
        # Sort the street index into a simple dictionary of     #
        # street name mapped to a list of which cells contain   #
        # parts of the street of that name                      #
        #########################################################

        # In the following, streetList is a dictionary with keys which
        # are cell IDs - the contents of the dictionary is a list of all
        # of the streets in a given cell.

        # StreeetIndexSorted is a dictionary with streetnames as the keys
        # The contents is a list of all of the cells that contain a way
        # of the given name.

        # self.StreetIndex is a tidied up version of StreetIndexSorted - the
        # contents is a displayable string showing which cells contain the
        # given street name.
        

        # Now we need to sort the street index so that we have a schedule
        # of streets identifying which cells the street is in.
        for cell in streetList:
            for street in streetList[cell]:
                streetName = street[1]
                if streetName != 'None':
                    if streetName in streetIndexSorted:
                        # Avoid multiple entries of the same cell for a
                        #   given street name - if it exists in the list,
                        # reject it, otherwise add it to the list..
                        try:
                            i = streetIndexSorted[streetName].index(cell)
                            if self.debug:
                                print "Rejected Duplicate Entry ",\
                                      streetName,cell,i
                        except:
                            streetIndexSorted[streetName].append(cell)
                    else:
                        streetIndexSorted[streetName] = [cell]


        streets = streetIndexSorted.keys()
        streets.sort()
        for street in streets:
            cellstr=""
            first = True
            cells = streetIndexSorted[street]
            cells.sort()
            for cell in cells:
                if first==True:
                    cellstr = "%s" % cell
                    first=False
                else:
                    cellstr = "%s, %s" % (cellstr,cell)
            self.streetIndex[street]=cellstr

    def expandWhereClause(self,whereclause):
        """Expands a string of the format
        title:column=val1|val2|val3 into a tuple:
        (title,column=val1 or column=val2 or column=val3)
        
        If the string does not contain a : specifying the title, it is
        set to the column name.
        
        04oct2009  GJ  ORIGINAL VERSION
        """
        # First look to see if there is a colon in the string.
        # NOTE that this means that you can not use a colon in your
        # whereclause if you do not specify the title!!!

        wc = whereclause
        i = wc.find(':')
        if i >= 0:
            # strip off the title and the remaining whereclause specification
            title=wc.split(':')[0]
            wc = wc.split(':')[1]
        else:
            #Set title to none - we assign it to the column name later
            title = None

        # Separate the column name from the list of values.
        column,vallist = wc.split('=')

        # If the title was not specified, set it to the column name.
        if title == None:
            title = column

        sql = None
        first = True
        for val in vallist.split('|'):
            if first == True:
                sql = "(%s=%s" % (column,val)
                first = False
            else:
                sql = "%s or %s=%s" % (sql,column,val)
        sql = "%s)" % sql
        return (title,sql)

    # db code
    def getBBContents(self,bbox,whereclause=None):
        """
        Returns all of the tagged nodes in the specified bounding box.
        If whereclause is provided, it appends a "where ...." statement
        to the SQL as a filter - it uses whereclause directly without
        any processing, so whereclause must be valid SQL.

        29sep2009  GJ ORIGINAL VERSION
        """
        # if self.debug:
        print "====== getBBContents: bbox=%s, whereclause=%s\n" %\
              (bbox,whereclause)

        #############################
        # First just look for nodes #
        #############################
        sqlstr = "select id,name,operator,amenity,shop,landuse,"\
                 "ST_Y(centroid(way)),ST_X(centroid(way))"\
                 "from planet_osm_point,planet_osm_nodes where id=osm_id and way && \
        SetSRID('BOX3D(%f %f,%f %f)'::box3d,900913)" % \
        (bbox.minx,bbox.miny,bbox.maxx,bbox.maxy) 

        if whereclause!=None:
            sqlstr = "%s and %s" % (sqlstr,whereclause)

        # if self.debug: print "sqlstr="+sqlstr
        
        #connection = psycopg.connect('dbname=mapnik', 'user=graham')
        # print "***Using user name %s." % self.uname
        connection = psycopg.connect('dbname=%s' % self.dbname,\
                                     'user=%s' % self.uname)
        mark = connection.cursor()
        mark.execute(sqlstr)
        record = mark.fetchall()

        if self.debug:
            if len(record)!=0: print "record=",record

        nodelist = record
        
        #######################################################
        # Now look for areas (polygons) with the desired tags #
        #######################################################
        sqlstr = "select osm_id,name,operator,amenity,shop,landuse,"\
                 "ST_Y(centroid(way)),ST_X(centroid(way)) "\
                 "from planet_osm_polygon where way && \
        SetSRID('BOX3D(%f %f,%f %f)'::box3d,900913)" % \
        (bbox.minx,bbox.miny,bbox.maxx,bbox.maxy) 

        if whereclause!=None:
            sqlstr = "%s and %s" % (sqlstr,whereclause)

        if self.debug: print "sqlstr="+sqlstr
        
        connection = psycopg.connect('dbname=%s' % self.dbname, 'user=%s' % self.uname)
        mark = connection.cursor()
        mark.execute(sqlstr)
        record = mark.fetchall()

        if self.debug:
            if len(record)!=0: print "record=",record

        waylist = record

        if len(waylist)>0:
            #print "waylist=",waylist
            for way in waylist:
                nodelist.append(way)
            #print "returning nodelist=",nodelist
            
        return nodelist


    def getBBStreets(self,bbox,whereclause=None):
        """
        Returns all of the streets in the specified bounding box.
        If whereclause is provided, it appends a "where ...." statement
        to the SQL as a filter - it uses whereclause directly without
        any processing, so whereclause must be valid SQL.

        03oct2009  GJ ORIGINAL VERSION
        """
        if self.debug: print "getBBStreets: bbox=%s, whereclause=%s\n" %\
           (bbox,whereclause)
        
        sqlstr = "select osm_id,name,ref from planet_osm_line where highway is not null and way && \
        SetSRID('BOX3D(%f %f,%f %f)'::box3d,900913) order by name" % \
        (bbox.minx,bbox.miny,bbox.maxx,bbox.maxy) 

        if whereclause!=None:
            sqlstr = "%s and %s" % (sqlstr,whereclause)

        if self.debug: print "sqlstr="+sqlstr
        
        connection = psycopg.connect('dbname=%s' % self.dbname,\
                                     'user=%s' % self.uname)
        mark = connection.cursor()
        mark.execute(sqlstr)
        record = mark.fetchall()

        if self.debug:
            if len(record)!=0: print "record=",record

        return record


    def populateDB(self):
        """
        Download the required data from the OSM server, and populate the
        postresql database with it.
        31dec2009  GJ  ORIGINAL VERSION
        """
        print "populateDB"
        
        #Convert the lat/long origin into mercator projection metres.
        prj = mapnik.Projection(self.srs)
        c0 = prj.forward(mapnik.Coord(self.lon,self.lat))

        c0.x += self.map_size_x * self.tilesize
        c0.y += self.map_size_y * self.tilesize

        c1 = prj.inverse(c0)
        lon=c1.x
        lat=c1.y
        print "before = (%f,%f)" % (self.lon,self.lat)
        print c1
        print "after  = (%f,%f)" % (lon,lat)

        if is_true(self.preferences_list['xapi']):
            # XAPI Server
            print 'Using OSM XAPI Server for data download'
            url="http://www.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f" %\
                 (self.lon,self.lat,lon,lat)
            # url="http://www.informationfreeway.org/api/0.6/map?bbox=%f,%f,%f,%f" %\
            #      (self.lon,self.lat,lon,lat)
        else:
            # Live OSM Server
            print 'Using live OSM Server for data download'
            url="http://www.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f" %\
                 (self.lon,self.lat,lon,lat)

        osmFile = "%s/townguide.osm" % (self.preferences_list['outdir'])

        os.system("wget %s -O %s" % (url,osmFile))

        if os.path.exists(osmFile):
            try:
                print 'Importing data into postgresql database....'
                osm2pgsqlStr = "osm2pgsql -m -S %s/%s -d %s -a %s" %\
                           (self.preferences_list['datadir'],
                            "default.style",
                            self.preferences_list['dbname'],
                            osmFile)
                print "Calling osm2pgsql with: %s" % osm2pgsqlStr
                retval = os.system(osm2pgsqlStr)
                if (retval==0):
                    print 'Data import complete.'
                else:
                    print 'osm2pgsql returned %d - exiting' % retval
                    # system.exit(-1)
            except:
                print "Exception Occurred running osm2pgsql"
                system.exit(-1)
        else:
            print "ERROR:  Failed to download OSM data"
            print "Aborting...."
            system.exit(-1)

    def showData(self):
        """ Display data stored in the townguide class on the
        terminal screen.
        """
        for featureStr in self.features:
            feature = featureStr.split('=')[1]

            if feature in self.amenities:
                print "=======%s======" % feature
                for rec in self.amenities[feature]:
                    print rec

        for feature in self.amenitiesSorted.keys():
            for name in self.amenitiesSorted[feature].keys():
                cellList = ""
                for cell in self.amenitiesSorted[feature][name]:
                    cellList = "%s%s " % (cellList,cell)
                print feature,name,cellList

    # Render methods for the plugins ========================================
    # FIXME: Maybe these can be changed into lambdas?
    
    def renderBook(self):
        self.drawOverviewMap(self.outdir)
        townguide_renderer = bookRenderer(self)
        townguide_renderer.render()

    def renderHTML(self):
        self.drawOverviewMap(self.outdir)
        townguide_renderer = htmlRenderer(self)
        townguide_renderer.render()

    def renderPoster(self):
        townguide_renderer = posterRenderer(self)
        townguide_renderer.render()

    def renderNewPoster(self):
        townguide_renderer = newPosterRenderer(self)
        townguide_renderer.render()

    # Plugin support: change 3
    def renderSimpleLandscape(self):
        townguide_renderer = simpleLandscapeRenderer(self)
        townguide_renderer.render()

    def renderSimplePoster(self):
        townguide_renderer = simplePosterRenderer(self)
        townguide_renderer.render()


# INIT ----------------------------------------------------------
if __name__ == "__main__":
    from optparse import OptionParser

    usage = "Usage %prog [options] filename"
    version = "SVN Revision $Rev: 73 $"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-f", "--file", dest="outfile",
                      help="filename to use for output",
                      metavar="FILE")
    parser.add_option("-v", "--verbose", action="store_true",dest="verbose",
                      help="Include verbose output")
    parser.add_option("-d", "--debug", action="store_true",dest="debug",
                      help="Include debug output")
    parser.set_defaults(
        outfile = "townguide.html",
        debug = False,
        verbose = False)
    (options,args)=parser.parse_args()
    
    if (options.debug):
        options.verbose = True
        print "options   = %s" % options
        print "arguments = %s" % args


    # print
    # print "Townguide Version %s" % version
    # print
    
    if len(args)==0:
        print "No configuration file specified - using a simple default configuration as an example."
        preferences_list = {'title':'townguide default output',
              'origin':'54.6466,-1.2619',
              'mapsize':'10,12',
              'tilesize':'1000',
              'features':'amenity=school,amenity=pub'}
    else:
        print "Using configuration file %s." % args[0]
        preferences = prefs()
        preferences_list = preferences.loadPrefs(args[0])

    # tg = townguide(54.6466,-1.2619,1000,10,12)
    # townguide_map = townguide(preferences)
    # townguide(preferences)
    townguide(preferences)
    
