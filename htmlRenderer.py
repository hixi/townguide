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

import sys
import os

class htmlRenderer(): 
    def __init__(self,tg):
        print "htmlRenderer.init()"
        self.tg = tg

        self.filenames = {\
            'Title':'index.html',\
            'Overview Map':'overview.html',\
            'Street Index':'streetindex.html',\
            'Features':'features.html'}

        if self.tg.debug: print self.filenames

                           

    def renderHTML(self):
        self.renderHTMLTitlePage()
        self.renderHTMLOverviewPage()
        self.renderHTMLStreetIndexPage()
        self.renderHTMLFeaturesPage()

    def renderHTMLHeader(self,f,title):
        f.write("<html>")
        f.write("<head>")
        f.write("<title>%s</title>" % title)
        f.write("</head>")
        f.write("<body>")
        f.write("<h1>Town Guide</h1>\n")
        f.write("<h1>%s</h1>\n" % self.tg.title)
        f.write("<hr/>")

    def renderHTMLFooter(self,f):
        f.write("</body>")
        f.write("</html>")

    def renderHTMLContents(self,f):
        f.write("<h2>Contents</h2>")
        f.write("<p>")
        for file in self.filenames:
            f.write("<a href='%s'>%s</a> " % \
                    (self.filenames[file],file))
        f.write("<br></p>")
        #f.write("<p>Detailed Maps<br>")
        #for y in range(0,self.tg.ny):
        #    for x in range(0,self.tg.nx):
        #        cellid = self.tg.cellLabel(x,y)
        #        fname = "%s.png" % (cellid)
        #        f.write("<a href='%s'>%s</a>," % (fname,cellid))
        #    f.write("<br>")
        #f.write("<p>")
        f.write("<hr>")

    def renderHTMLTitlePage(self):
        outpath = "%s/%s" % (self.tg.outdir,self.filenames['Title'])
        f = open(outpath,"w")
        imgpath="%s/%s" % (os.path.dirname(os.path.realpath(__file__)),\
                           "images")
        print imgpath
        self.renderHTMLHeader(f,self.tg.title)
        self.renderHTMLContents(f)

        f.write("<p>This program uses data provided by ")
        f.write("<a href='http://www.openstreetmap.org'><img src='%s/%s'></a>." %\
                (imgpath,"Osm_linkage.png"))
        f.write("</p>")
        f.write("<p><a href='http://www.openstreetmap.org'>OpenStreetMap</a>")
        f.write(" data is provided freely by volunteers. ")
        f.write("When you identify errors or omissions in the data,")
        f.write("please report them at <a href='http://www.openstreetbugs.org'>")
        f.write("OpenStreetBugs</a>, or join ")
        f.write(" <a href='http://www.openstreetmap.org'>OpenStreetMap</a>")
        f.write(" and improve the data yourself!</p>")
        f.write("<p>This page was produced by ")
        f.write("<a href='http://code.google.com/p/ntmisc'>townguide.py</a>.</p>")
        f.write("<p>Copyright Graham Jones, 2009<p>")
               

        self.renderHTMLFooter(f)

        f.close()


    def renderHTMLOverviewPage(self):
        outpath = "%s/%s" % (self.tg.outdir,self.filenames['Overview Map'])
        f = open(outpath,"w")
        self.renderHTMLHeader(f,self.tg.title)
        self.renderHTMLContents(f)
        f.write("<image src='overview.png' usemap='#tiles'/>")

        # Add an image map to link to the detailed tile images
        f.write("<map name='tiles'>")
        for y in range(0,self.tg.ny):
            for x in range(0,self.tg.nx):
                cellid = self.tg.cellLabel(x,y)
                fname = "%s.png" % (cellid)
                f.write("<area shape='rect' coords='%d,%d,%d,%d' href='%s'>" %\
                        (int(x*self.tg.slen/self.tg.oscale),\
                        int((self.tg.ny-y-1)*self.tg.slen/self.tg.oscale),\
                        int((x+1)*self.tg.slen/self.tg.oscale),\
                        int((self.tg.ny-y)*self.tg.slen/self.tg.oscale),\
                        fname))
        f.write("</map>")
        self.renderHTMLFooter(f)
        self.renderHTMLContents(f)
        f.close()

    def renderHTMLStreetIndexPage(self):
        outpath = "%s/%s" % (self.tg.outdir,self.filenames['Street Index'])
        f = open(outpath,"w")
        self.renderHTMLHeader(f,self.tg.title)
        self.renderHTMLContents(f)

        # render the streets in aphabetical order
        streets = self.tg.streetIndex.keys()
        streets.sort()
        for street in streets:
            f.write("%s (%s)<br>" % (street,self.tg.streetIndex[street]))

        self.renderHTMLFooter(f)
        self.renderHTMLContents(f)
        f.close()

    def renderHTMLFeaturesPage(self):
        outpath = "%s/%s" % (self.tg.outdir,self.filenames['Features'])
        f = open(outpath,"w")
        self.renderHTMLHeader(f,self.tg.title)
        self.renderHTMLContents(f)
        f.write("<h1>Features</h1>")
        #for featureStr in self.features:
        #    feature = featureStr.split('=')[1]
        featurelist = self.tg.amenitiesSorted.keys()
        featurelist.sort()
        for feature in featurelist:
            f.write("<h2>%s</h2>" % feature)
            names = self.tg.amenitiesSorted[feature].keys()
            names.sort()
            for name in names:
                first=True
                for cell in self.tg.amenitiesSorted[feature][name]:
                    if first:
                        cellList = cell
                        first=False
                    else:
                        cellList = "%s, %s" % (cellList,cell)
                if name==None:
                    f.write("%s (%s) <br>\n" % ("Un-Named",cellList))
                else:
                    f.write("%s (%s) <br>\n" % (name,cellList))
                    
        self.renderHTMLFooter(f)
        f.close()
        self.renderHTMLCellFeaturesTables()

    def renderHTMLCellFeaturesTables(self):
        for y in range(0,self.tg.ny):
            for x in range(0,self.tg.nx):
                cellid = self.tg.cellLabel(x,y)
                fname = "%s.html" % (cellid)
                outpath = "%s/%s" % (self.tg.outdir,fname)
                f = open(outpath,"w")
                self.renderHTMLHeader(f,self.tg.title)
                f.write("<h1>Features in Cell %s</h1>" % cellid)

                featurelist = self.tg.amenitiesSorted.keys()
                featurelist.sort()
                for feature in featurelist:
                    f.write("<h2>%s</h2>" % feature)
                    names = self.tg.amenitiesSorted[feature].keys()
                    names.sort()
                    for name in names:
                        first=True
                        for cell in self.tg.amenitiesSorted[feature][name]:
                            if (cell==cellid):
                                if name==None:
                                    f.write("%s (%s) <br>\n" % ("Un-Named",cell))
                                else:
                                    f.write("%s (%s) <br>\n" % (name,cell))
                    
                self.renderHTMLFooter(f)
                f.close()


    def render(self):
        print "htmlRenderer.render()"
        self.renderHTML()
