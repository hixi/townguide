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

mapsize - (int(nx), int(ny) - the size of the region in number of tiles in the x and y direction.

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

$LastChangedDate$
$Rev$
$Author$
"""
from prefs import prefs
import sys
import psycopg2 as psycopg
import mapnik
import Image, ImageDraw, ImageFont
import os
import string
from posterRenderer import posterRenderer
from htmlRenderer import htmlRenderer
from bookRenderer import bookRenderer

class townguide:
    """
    The main townguide program is stored in the townguide class.
    As written this is pretty pointless, but I think I will need this
    when I implement output plugins to do rendering and want to pass
    all of the data to the plugin.
    
    """
    def __init__(self,pr):
        """Initialise the townguide generating class from the set of
        preferences specified in the dictionary 'pl'.   The required data
        is then extracted from the database, and the selected output renderer
        called.
        """
        defaults={
            'debug': 'False',
            'origin': '54.6466,-1.2619',
            'mapzize': '3,3',
            'tilesize': '1000',
            'oscale': '10',
            'datadir': '/home/disk2/graham/ntmisc/townguide',
            'mapfile': '/home/disk2/graham/ntmisc/townguide/osm.xml',
            'uname': 'graham',
            'dbname': 'mapnik',
            'download': 'False',
            'xapi': 'True',
            'features': "Banking:amenity='bank'|'atm',"\
            "Shopping:shop='mall'|'supermarket'|'convenience'|'alcohol'|'baker'"

            }

        self.pr = pr
        self.pr.applyDefaults(defaults)
        pl = pr.getPrefs()
        if pl['debug']=='True'\
                        or pl['debug']=='true'\
                        or pl['debug']=='TRUE':
            self.debug=True
        else:
            self.debug=False


        (lat,lon) = pl['origin'].split(',')
        lon = float(lon)
        lat = float(lat)
        (nx,ny)   = pl['mapsize'].split(',')
        nx = int(nx)
        ny = int(ny)
        slen      = float(pl['tilesize'])
        oscale = float(pl['oscale'])

        # self.features is the list of map features to be presented.
        self.features = []
        featstrs = pl['features'].split(',')
        for feat in featstrs:
            self.features.append(str(feat.strip()))
        if self.debug: print self.features

        if self.debug: print "lat=%f, lon=%f, nx=%d, ny=%d" % (lat,lon,nx,ny)

        #Convert the lat/long origin into mercator projection metres.
        prj = mapnik.Projection("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over")
        self.c0 = prj.forward(mapnik.Coord(lon,lat))

        print "Origin (%f,%f) is equivalent to (%f,%f) in projection" %\
              (lon,lat,self.c0.x,self.c0.y)

        self.lat = lat
        self.lon = lon

        self.pl = pl
        self.nx = nx
        self.ny = ny
        self.slen = slen
        self.tilesize = float(pl['tilesize'])
        self.oscale = oscale
        self.uname = pl['uname']
        self.dbname = pl['dbname']

        self.title = pl['title']
        self.outdir = pl['outdir']

        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        downloadStr = pl['download']
        downloadStr = downloadStr.lower()
        print "downloadstr = %s" % downloadStr

        if downloadStr == 'true':
            self.populateDB()



        print "Extracting Map Features from Database"
        self.streetIndex = {}
        self.amenities = {}
        self.amenitiesSorted = {}
        self.getAmenities()
        

        if pl['format']=='html':
            print "Rendering html map and text"
            self.drawOverviewMap(self.outdir)
            tr = htmlRenderer(self)
            tr.render()
            #self.renderHTML()
        elif pl['format']=='pdf':
            #self.renderPDF()
            self.drawOverviewMap(self.outdir)
            tr = bookRenderer(self)
            tr.render()
        elif pl['format']=='poster':
            tr = posterRenderer(self)
            tr.render()
        else:
            print "ERROR - Unrecognised Format %s." % pl['format']


      #  self.showData()


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
        #for cell in self.streetIndex:
        #    for street in cell:
        #        print "%s (%s)" % (street,cell)
                    



        
    def drawTile(self,bbox,imgx,imgy,fname):
        """Call Mapnik to draw a map image for data in
        bounding box bbox.  The image size is imgx by imgy pixels, and
        the output filename is fname.

        29sep2009  GJ  ORIGINAL VERSION, based on generate_image.py
        """
        #try:
        #    mapfile = mapnik.os.environ['MAPNIK_MAP_FILE']
        #except KeyError:
        #    mapfile = "osm.xml"
        #mapfile = "osm.xml"
        mapfile = str(self.pl['mapfile'])
        map_uri = str(fname)

        m = mapnik.Map(imgx,imgy)
        mapnik.load_map(m,mapfile)
        m.zoom_to_box(bbox)
        im = mapnik.Image(imgx,imgy)
        mapnik.render(m, im)
        view = im.view(0,0,imgx,imgy) # x,y,width,height
        view.save(map_uri,'png')


            
    def drawOverviewMap(self,outdir='',addFeatures=False):
        """Draws the overview map of the full area requested and
        adds a grid with row and column identifiers to the map image.
        29sep2009  GJ ORIGINAL VERSION
        01jan2010  Added option to add feature markers to map.
        """
        # First draw the basic map using mapnik.
        fname = "%s/overview.png" % outdir

        if self.debug: print "Drawing Overview Map - fname=",fname
        scale = self.oscale # metres per pixel
        c0 = self.c0
        bbox = mapnik.Envelope(c0.x,\
                               c0.y,\
                               c0.x+self.slen*self.nx,\
                               c0.y+self.slen*self.ny)
        self.drawTile(bbox,
                      int(self.slen*self.nx/scale),
                      int(self.slen*self.ny/scale),
                      fname)

        # Now add the grid and labels
        im = Image.open(fname)
        draw = ImageDraw.Draw(im)
        fnt = ImageFont.truetype("%s/FreeSerif.ttf" % self.pl['datadir'], 12)
        for x in range(0,self.nx):
            xpx = x*self.slen/scale
            draw.line((xpx,0,xpx,im.size[1]), fill='white')
            str = self.xLabel(x)
            draw.text((xpx+self.slen/scale/2,12),
                      str,
                      font=fnt,
                      fill='black')
            draw.text((xpx+self.slen/scale/2,im.size[1]-24),
                      str,
                      font=fnt,
                      fill='black')
        for y in range(0,self.ny):
            ypx = (self.ny-y-1)*self.slen/scale
            draw.line((0,ypx,im.size[0],ypx), fill='white')
            str = self.yLabel(y)
            draw.text((12,ypx+self.slen/scale/2),
                      str,
                      font=fnt,
                      fill='black')
            draw.text((im.size[0]-24,ypx+self.slen/scale/2),
                      str,
                      font=fnt,
                      fill='black')

        if addFeatures:
            print "adding feature markers to map..."
            featurelist = self.amenities.keys()
            featurelist.sort()
            featureNo = 1
            for feature in featurelist:
                for rec in self.amenities[feature]:
                    print rec
                    if len(rec[2])==8:
                        fx = rec[2][7]
                        fy = rec[2][6]
                    else:
                        print "****ERROR - No Location for record ",rec,"*****"
                        print "This is probably because this PoI is an area, not a node"
                        print "I will fix this eventually!!!"
                        fx = self.c0.x
                        fy = self.c0.y
                    imx = int((fx - self.c0.x)/scale)
                    imy = im.size[1] - int((fy - self.c0.y)/scale)
                    #print "fx=%d imx=%d c0.x=%d, fy=%d imy=%d c0.y=%d, scale=%f" %\
                    #      (fx,imx,self.c0.x,fy,imy,self.c0.y, scale)
                    draw.ellipse((imx-6,imy-6,imx+18,imy+18),
                                 fill='yellow',
                                 outline='black')
                    draw.text((imx,imy),
                              "%d" % featureNo,
                              font=fnt,
                              fill='black')
                    featureNo+=1


        del draw
        f = open(fname,'w')
        im.save(f,"PNG")
        f.close()



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
        return "%s%s" % (self.xLabel(x),\
                         self.yLabel(y))

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
        c0 = self.c0
        streetList = {}
        streetIndexSorted = {}
        
        for tx in range(0,self.nx):
            minx = c0.x + self.slen * tx
            for ty in range(0,self.ny):
                sys.stdout.write("%s, " % self.cellLabel(tx,ty))
                sys.stdout.flush()
                miny = c0.y + self.slen * ty
                bbox = mapnik.Envelope(minx,\
                                       miny,\
                                       minx+self.slen,\
                                       miny+self.slen)
                fname = "image_%02d_%02d.png" % (tx,ty)
                #if self.debug: print bbox

                ########################################################
                # Extract points of interest into amenities dictionary #
                ########################################################
                for featureStr in self.features:
                    title,wc = self.expandWhereClause(featureStr)
                    #feature = featureStr.split('=')[1]
                    feature = title
                    if self.debug: print "Extracting feature %s using %s." %\
                       (feature,featureStr)
                    pois = self.getBBContents(bbox,wc)
                    for poi in pois:
                        if feature in self.amenities:
                            self.amenities[feature].append((tx,ty,poi))
                        else:
                            self.amenities[feature]=[(tx,ty,poi)]


                ##############################################
                # Extract all of the streetnames in the cell #
                ##############################################
                bbStreets = self.getBBStreets(bbox)
                streetList[self.cellLabel(tx,ty)]=bbStreets

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
            for poi in self.amenities[feature]:
                cellId = self.cellLabel(poi[0],poi[1])
                osm_id = poi[2][0]
                name = poi[2][1]
                operator = poi[2][2]
                amenityVal = poi[2][3]
                shopVal = poi[2][4]
                landuse = poi[2][5]
                if name==None:
                    if amenityVal==None:
                        if shopVal==None:
                            if landuse==None:
                                name = "Unidentified thing - osm_id=%d" % osm_id
                            else:
                                name = "Unnamed %s" % landuse
                        else:
                            name = "Unnamed %s" % shopVal
                    else:
                        name = "Unnamed %s" % amenityVal
                print "%s %s %s" % (feature, name, cellId)
                if not feature in self.amenitiesSorted:
                    print "creating dictionary for feature %s" % feature
                    self.amenitiesSorted[feature]={}
                if name in self.amenitiesSorted[feature]:
                    print "dictionary %s already exists in feature %s" %\
                          (name,feature)
                    if not cellId in self.amenitiesSorted[feature][name]:
                        print "appending cellid"
                        self.amenitiesSorted[feature][name].append(cellId)
                    else:
                        print "skipping duplicate feature %s %s in %s\n" %\
                              (feature,name,cellId)
                else:
                    print "adding cell id to list"
                    self.amenitiesSorted[feature][name] = [cellId]
                    print "self.amenitiesSorted=", \
                          self.amenitiesSorted[feature][name]

        


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
        #First look to see if there is a colon in the string.
        # NOTE that this means that you can not use a colon in your
        # whereclause if you do not specify the title!!!

        wc = whereclause
        i = wc.find(':')
        if i>=0:
            #strip off the title and the remaining whereclause specification
            title=wc.split(':')[0]
            wc = wc.split(':')[1]
        else:
            #Set title to none - we assign it to the column name later
            title=None

        # Separate the column name from the list of values.
        column,vallist = wc.split('=')

        # If the title was not specified, set it to the column name.
        if title==None:
            title=column

        sql=None
        first=True
        for val in vallist.split('|'):
            if first==True:
                sql = "(%s=%s" % (column,val)
                first=False
            else:
                sql = "%s or %s=%s" % (sql,column,val)
        sql = "%s)" % sql
        return (title,sql)


    def getBBContents(self,bbox,whereclause=None):
        """
        Returns all of the tagged nodes in the specified bounding box.
        If whereclause is provided, it appends a "where ...." statement
        to the SQL as a filter - it uses whereclause directly without
        any processing, so whereclause must be valid SQL.

        29sep2009  GJ ORIGINAL VERSION
        """
        if self.debug: print "getBBContents: bbox=%s, whereclause=%s\n" %\
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

        if self.debug: print "sqlstr="+sqlstr
        
        #connection = psycopg.connect('dbname=mapnik', 'user=graham')
        print "***Using user name %s." % self.uname
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
        
        connection = psycopg.connect('dbname=%s' % self.dbname,\
                                     'user=%s' % self.uname)
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
        
        #connection = psycopg.connect('dbname=mapnik', 'user=graham')
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
        prj = mapnik.Projection("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over")
        c0 = prj.forward(mapnik.Coord(self.lon,self.lat))

        c0.x += self.nx * self.tilesize
        c0.y += self.ny * self.tilesize

        c1 = prj.inverse(c0)
        lon=c1.x
        lat=c1.y
        print "before = (%f,%f)" % (self.lon,self.lat)
        print c1
        print "after  = (%f,%f)" % (lon,lat)

        if self.pl['xapi'].lower() == 'true':
            # XAPI Server
            print 'Using OSM XAPI Server for data download'
            url="http://www.informationfreeway.org/api/0.6/map?bbox=%f,%f,%f,%f" %\
                 (self.lon,self.lat,lon,lat)
        else:
            # Live OSM Server
            print 'Using live OSM Server for data download'
            url="http://www.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f" %\
                 (self.lon,self.lat,lon,lat)

        os.system("wget %s -O %s/townguide.osm" % (url,self.pl['outdir']))

        print 'Importing data into postgresql database....'
        osm2pgsqlStr = "osm2pgsql -m -S %s/%s -d %s -s %s/townguide.osm" %\
                  (self.pl['datadir'],
                   "default.style",
                   self.pl['dbname'],
                   self.pl['outdir'])
        print "Calling osm2pgsql with: %s" % osm2pgsqlStr
        
        os.system(osm2pgsqlStr)

        print 'Data import complete.'


if __name__ == "__main__":
    from optparse import OptionParser

    usage = "Usage %prog [options] filename"
    version = "SVN Revision $Rev$"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-f", "--file", dest="outfile",
                      help="filename to use for output",
                      metavar="FILE")
    parser.add_option("-v", "--verbose", action="store_true",dest="verbose",
                      help="Include verbose output")
    parser.add_option("-d", "--debug", action="store_true",dest="debug",
                      help="Include debug output")
    parser.set_defaults(
        outfile="townguide.html",
        debug=False,
        verbose=False)
    (options,args)=parser.parse_args()
    
    if (options.debug):
        options.verbose = True
        print "options   = %s" % options
        print "arguments = %s" % args


    print
    print "Townguide Version %s" % version
    print
    
    if len(args)==0:
        print "No configuration file specified - using a simple default\
configuration as an example."
        pl = {'title':'townguide default output',
              'origin':'54.6466,-1.2619',
              'mapsize':'10,12',
              'tilesize':'1000',
              'features':'amenity=school,amenity=pub'}
    else:
        print "Using configuration file %s." % args[0]
        pr = prefs()
        pl = pr.loadPrefs(args[0])


    #tg = townguide(54.6466,-1.2619,1000,10,12)
    tg = townguide(pr)
        
