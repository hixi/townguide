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
import reportlab.platypus as platypus 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm
from reportlab.lib import pagesizes
from reportlab.graphics.shapes import Rect
# from reportlab.lib.colors import *

# Register unicode font 
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from townguide.defaults import get_unifont_path
unifont = TTFont('unifont', get_unifont_path())
pdfmetrics.registerFont(    unifont    )

class newPosterRenderer():
    """
    A townguide plugin to produce a poster showing a map and street index
    as a PDF file.
    It uses the reportlab platypus library to produce the PDF file.
    A lot of useful information was found at
    http://www.hoboes.com/Mimsy/hacks/multiple-column-pdf/, for which I am
    extremely grateful.

    """
    
    def __init__(self, townguide):
        """
        Initialise the posterRenderer - called by townguide.py
        tg should be the instance of townguide used to call this function.
        It is used to provide the user selectable parameters as the
        townguide.preferences_list[] dictionary.
        The following paramaters are used from the tg.preferences_list[] dictionary:
         - pagesize : the required output page size (A4, A3 etc) - default A4
         - mapvfrac : the vertical fraction of the page to be filled by the map (%) - default 80
        """
        # print "posterRenderer.init()"
        self.townguide = townguide

        # Maybe handle this with Python ConfigParser
        defPrefs = {
            'pagesize': 'A4',
            'description': 'No Description Provided',
            'mapvfrac': '80',
            'dpi':'100',
            'bottomMargin': '30',
            'topMargin': '72',
            'leftMargin': '10',
            'rightMargin': '10',
            'titleFrameHeight': '0',
            'columnWidth': '5',
            'streetIndex': 'True',
            'featureList': 'True',
            'features': "Banking:amenity='bank'|'atm',"\
            "Shopping:shop='mall'|'supermarket'|'convenience'|'alcohol'|'baker'"
            }

        townguide.preferences.applyDefaults(defPrefs)
        
        self.setStyles()




    def setStyles(self):
        pageSizeDict = {
            'letter': pagesizes.letter,
            'A6': pagesizes.A6,
            'A5': pagesizes.A5,
            'A4': pagesizes.A4,
            'A3': pagesizes.A3,
            'A2': pagesizes.A2,
            'A1': pagesizes.A1,
            'A0': pagesizes.A0
            }
        self.pagesize = pageSizeDict.get(self.townguide.preferences_list['pagesize'])

        if self.pagesize == None:
            print ("ERROR - Pagesize %s unrecognised - Using A4 instead\n" % ps_str)
            self.pagesize = pagesizes.A4

        (self.pageX,self.pageY) = self.pagesize

        print "pagesize = %f, %f" % (self.pageX, self.pageY)

        self.styles = getSampleStyleSheet()

        #print dir(self.styles)
        #self.styles.list()

        self.mf = float(self.townguide.preferences_list['mapvfrac'])/100.
        self.topMargin=int(self.townguide.preferences_list['topMargin'])
        self.bottomMargin=int(self.townguide.preferences_list['bottomMargin'])
        self.leftMargin=int(self.townguide.preferences_list['leftMargin'])
        self.rightMargin=int(self.townguide.preferences_list['rightMargin'])

        self.titleFrameHeight = int(self.townguide.preferences_list['titleFrameHeight'])
        self.columnWidth = float(self.townguide.preferences_list['columnWidth'])
        
        self.titleStyle = self.styles["Title"]
        self.titleStyle.fontSize = 40
        self.titleStyle.fontSize * 1.1


    def render(self):
        # print "posterRenderer.render()"
        outpath = "%s/townguide_poster.pdf" % self.townguide.outdir

        # doc = platypus.BaseDocTemplate(outpath,pagesize=self.pagesize)
        doc = platypus.BaseDocTemplate(outpath,pagesize=self.pagesize)
        doc.leftMargin = self.leftMargin
        doc.rightMargin = self.rightMargin
        doc.topMargin = self.topMargin
        doc.bottomMargin = self.bottomMargin
        doc.width = self.pagesize[0] - self.leftMargin - self.rightMargin
        doc.height = self.pagesize[1] - self.topMargin - self.bottomMargin

        # mapframe spans whole page and goes to half way down the page
        print "self.mf=%f." % self.mf
        mapframe = platypus.Frame(doc.leftMargin,
                                  doc.bottomMargin + doc.height*(1-self.mf) - self.titleFrameHeight,
                                  doc.width,
                                  doc.height * self.mf,
                                  showBoundary=True,
                                  leftPadding=0,
                                  rightPadding=0,
                                  topPadding=0,
                                  bottomPadding=0)

        # Now work out how big the actual map will be (depends on the
        #   aspect ratio of the area to be mapped).
        self.mapY = mapframe.height - mapframe.topPadding - mapframe.bottomPadding
        self.mapX = self.mapY * self.townguide.map_size_x / self.townguide.map_size_y
        
        if (self.mapX > (mapframe.width-mapframe.leftPadding-mapframe.rightPadding)):
            self.mapX = mapframe.width - mapframe.leftPadding - mapframe.rightPadding
            self.mapY = self.mapX * self.townguide.map_size_y/self.townguide.map_size_x
        print "mapsize = %f, %f points" % (self.mapX, self.mapY)

        # how much space is there next to the map - can we fit some columns
        # in there?
        sparew = mapframe.width + mapframe.leftPadding + mapframe.rightPadding - self.mapX
        mapframe.width -= sparew

        #firstPageFrames = [titleframe,mapframe]
        firstPageFrames = [mapframe]

        if sparew > self.columnWidth*cm:
            print "adding extra frames next to map"
            colCount = int(sparew / (self.columnWidth*cm))
            colWidth = (sparew)/colCount
            colHeight = doc.height*self.mf   #same as map.

            for colNo in range(colCount):
                leftMargin = doc.leftMargin \
                             + mapframe.width \
                             + mapframe.leftPadding \
                             + mapframe.rightPadding \
                             + colNo * colWidth
                column = platypus.Frame(leftMargin,
                                        doc.bottomMargin + doc.height * (1 - self.mf) - self.titleFrameHeight,
                                        colWidth,colHeight,
                                        showBoundary=True)
                firstPageFrames.append(column)


        # the columns occupy the bottom half of the page.
        colCount = int(doc.width / (self.columnWidth*cm))
        colWidth = (doc.width)/colCount
        colHeight = doc.height * (1 - self.mf) - self.titleFrameHeight

        for colNo in range(colCount):
            leftMargin = doc.leftMargin + colNo*colWidth
            column = platypus.Frame(leftMargin,doc.bottomMargin,
                                    colWidth,colHeight,
                                    showBoundary=True)
            firstPageFrames.append(column)


        # Set up the overflow pages - just the title frame and columns.
        overflowPageFrames = []
        colHeight = doc.height 
        for colNo in range(colCount):
            leftMargin = doc.leftMargin + colNo*colWidth
            column = platypus.Frame(leftMargin,doc.bottomMargin,
                                    colWidth,colHeight,
                                    showBoundary=True)
            overflowPageFrames.append(column)
        

        templates = [platypus.PageTemplate(frames=firstPageFrames,
                                           id="first",
                                           onPage = self.decoratePage),
                     platypus.PageTemplate(frames=overflowPageFrames,
                                           id="overflow",
                                           onPage = self.decoratePage)
                     ]
        doc.addPageTemplates(templates)
        ##############################################################
        #          Now Add the Content                               #
        ##############################################################
        
        Story = []
        
        #Story.append(platypus.Paragraph(self.tg.title,self.styles["Title"]))
        #Story.append(platypus.FrameBreak())
                     
        style = self.styles["Normal"]

        ###############################################################
        # Render the map, and add it to the page

        #self.townguide.preferences_list['oscale'] =  1000. *  self.tg.nx / self.mapX / 2
        # dpi = 300 # required image resolution
        dpi = float(self.townguide.preferences_list['dpi'])
        pixels = self.mapX * dpi / 72.  # number of pixels in image at required resolution
        # oscale is metres per pixel
        self.townguide.preferences_list['oscale'] =  self.townguide.preferences_list['tilesize'] * self.townguide.preferences_list['map_size_x'] / pixels
        print "pixels = %f" % pixels
        self.townguide.drawOverviewMap(self.townguide.outdir,addFeatures=True)

        im = Image("%s/%s" % (self.townguide.outdir,"overview.png"),
                   width=self.mapX, height=self.mapY)
        im.hAlign = 'CENTER'
        Story.append(im)
        

        # Add description paragraph ========================================
        style.fontName = "Helvetica-Bold"
        description_bold = Paragraph("Information", style)
        Story.append(description_bold)
        
        # description text
        style.fontName = "unifont"
        description = Paragraph(self.townguide.preferences_list['description'], style)
        Story.append(description)

        # Once we have rendered the map image, we need to go to the next frame.
        Story.append(platypus.FrameBreak())
        Story.append(platypus.NextPageTemplate("overflow"))

        ################################################################
        # render the streets in aphabetical order
        if self.townguide.preferences_list['streetIndex'].lower()=='true':
            style.fontName = "Helvetica-Bold"
            Story.append(platypus.Paragraph("Street Index",style))
            
            style.fontName = "unifont"
            streets = self.townguide.streetIndex.keys()
            streets.sort()
            for street in streets:
                p = Paragraph("%s (%s)" % (street,self.townguide.streetIndex[street]),style)
                Story.append(p)


        if self.townguide.preferences_list['featureList'].lower()=='true':
            #Do not do a frame break if this is the first frame.
            if self.townguide.preferences_list['streetIndex'].lower()=='true':
                Story.append(platypus.FrameBreak())
            style.fontName = "Helvetica-Bold"
            Story.append(platypus.Paragraph("Points of Interest",style))
            style.fontName = "unifont"
            featurelist = self.townguide.amenities.keys()
            #print self.townguide.amenities
            featurelist.sort()
            featureNo = 1
            for feature in featurelist:
                style.fontName = "unifont"
                Story.append(platypus.Paragraph(feature,style))
                style.fontName = "unifont"
                for rec in self.townguide.amenities[feature]:
                    #print rec
                    lbl = self.townguide.cellLabel(rec[0],rec[1])
                    name = rec[2][1]
                    p = Paragraph("%d: %s (%s)" % (featureNo,name,lbl),style)
                    Story.append(p)
                    featureNo += 1

        if self.townguide.preferences_list['debug'].lower()=='true': 
            # This adds some padding to test the overflow page function.
            for n in range(100):
                p = Paragraph("Para %d - switch off debug mode to remove!!" % n,style)
                Story.append(p)

        # This line is important - it actually generates the PDF file.
        doc.build(Story)   


    def decoratePage(self,canvas,doc):
        print "decoratePage"
        PAGE_HEIGHT=self.pagesize[1]; PAGE_WIDTH=self.pagesize[0]
        canvas.saveState()
        # canvas.setFillColorRGB(0.9,0.9,0.9)
        canvas.setFillColor("#FFFFFF")
        canvas.rect(5, 5, PAGE_WIDTH-10, PAGE_HEIGHT-10,fill=1)
        canvas.restoreState()
        canvas.saveState()
        canvas.setFont('Helvetica-Bold',16)
        
        # Drawing the title
        canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT - (doc.topMargin/2), self.townguide.title)
        canvas.setFont('Helvetica',9)
        canvas.drawString(doc.leftMargin, (doc.bottomMargin/2), "Page %s" % doc.page)
        revStr = "$Rev: 52 $"
        revStr = revStr.split(':')[1]
        revStr = revStr.split('$')[0]
        
        # Footer
        canvas.drawRightString(doc.leftMargin + doc.width, (doc.bottomMargin/2),
                               "Output Produced by townguide newPosterRenderer "\
                               "Version %s.       Map data (c) OpenStreetMap and "\
                               "contributors, CC-BY-SA" % revStr)
        canvas.restoreState()

#_. Dummy outline topic header -- see`allout-mode' docstring: `^Hm'.
#_. Local emacs vars.
#_ , Local variables:
#_ , allout-layout: (-1 : 0)
#_ , End:

