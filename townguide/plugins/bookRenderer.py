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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import reportlab.lib.styles as styles
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm
from reportlab.lib import pagesizes
from reportlab.platypus.flowables import KeepInFrame 
from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import *



class bookRenderer():
    """
    A townguide plugin to produce a booklet containing an overview map,
    detailed large scale maps, street index and identify selected map features
    as a PDF file.
    It uses the reportlab platypus library to produce the PDF file.
    A lot of useful information was found at
    http://www.hoboes.com/Mimsy/hacks/multiple-column-pdf/, for which I am
    extremely grateful.

    """
    def __init__(self,townguide):
        """
        Initialise the bookRenderer - called by townguide.py
        tg should be the instance of townguide used to call this function.
        It is used to provide the user selectable parameters as the
        tg.pl[] dictionary.
        The following paramaters are used from the tg.preferences_list[] dictionary:
         - pagesize : the required output page size (A4, A3 etc) - default A4
         - mapvfrac : the vertical fraction of the page to be filled by the map (%) - default 80
        """
        print "bookRenderer.init()"
        self.townguide = townguide

        defPrefs = {
            'imagePath': '/home/mariko/proyectos/GSoC/townguide-py/styles/symbols/',
            'pagesize': 'A4',
            'mapvfrac': '80',
            'bottomMargin': '30',
            'topMargin': '72',
            'leftMargin': '10',
            'rightMargin': '10',
            'titleFrameHeight': '50',
            'logoFrac': '30',        # Vertical fraction of front page for logo
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
            print ("ERROR - Pagesize %s unrecognised - Using A4 instead\n" \
                   % ps_str)
            self.pagesize = pagesizes.A4

        (self.pageX,self.pageY) = self.pagesize

        print "pagesize = %f, %f" % (self.pageX,self.pageY)
                

        self.styles = styles.getSampleStyleSheet()

        #print dir(self.styles)
        #self.styles.list()

        self.mf = float(self.townguide.preferences_list['mapvfrac'])/100.
        self.topMargin=int(self.townguide.preferences_list['topMargin'])
        self.bottomMargin=int(self.townguide.preferences_list['bottomMargin'])
        self.leftMargin=int(self.townguide.preferences_list['leftMargin'])
        self.rightMargin=int(self.townguide.preferences_list['leftMargin'])

        self.titleFrameHeight = int(self.townguide.preferences_list['titleFrameHeight'])
        self.columnWidth = float(self.townguide.preferences_list['columnWidth'])
        
        self.titleStyle = self.styles["Title"]
        self.titleStyle.fontSize = 40
        self.titleStyle.fontSize*1.1


    def render(self):
        print "bookRenderer.render()"
        outpath = "%s/townguide_book.pdf" % self.townguide.outdir

        doc = platypus.BaseDocTemplate(outpath,pagesize=self.pagesize)
        doc.leftMargin = self.leftMargin
        doc.rightMargin = self.rightMargin
        doc.topMargin = self.topMargin
        doc.bottomMargin = self.bottomMargin
        doc.width = self.pagesize[0] - self.leftMargin - self.rightMargin
        doc.height = self.pagesize[1] - self.topMargin - self.bottomMargin

        ##################################
        # Set up the front page template #
        ##################################
        # titleframe spans whole page.
        titleframe = platypus.Frame(doc.leftMargin,\
                                  doc.bottomMargin+doc.height\
                                    - self.titleFrameHeight,\
                                  doc.width,\
                                  self.titleFrameHeight,\
                                  showBoundary=True)
        lf = float(self.townguide.preferences_list['logoFrac'])/100.
        logoframe= platypus.Frame(doc.leftMargin,\
                                  doc.bottomMargin \
                                  + doc.height*(1-lf)\
                                  - self.titleFrameHeight,\
                                  doc.width,\
                                  doc.height*lf,\
                                  showBoundary=True,
                                  leftPadding=0,
                                  rightPadding=0,
                                  topPadding=0,
                                  bottomPadding=0)

        frontPageFrames = [titleframe,logoframe]




        #####################################################
        # Set up the second (OSM information) page Template #
        #####################################################
        titleframe = platypus.Frame(doc.leftMargin,\
                                  doc.bottomMargin+doc.height\
                                    - self.titleFrameHeight,\
                                  doc.width,\
                                  self.titleFrameHeight,\
                                  showBoundary=True)
        bodyframe = platypus.Frame(doc.leftMargin,\
                                  doc.bottomMargin, \
                                  doc.width,\
                                  doc.height - self.titleFrameHeight,\
                                  showBoundary=True,
                                  leftPadding=0,
                                  rightPadding=0,
                                  topPadding=0,
                                  bottomPadding=0)

        infoPageFrames=[titleframe,bodyframe]


        #########################################
        # Set up the Overview Map Page Template #
        #########################################
        
        # mapframe spans whole page and goes to half way down the page
        print "self.mf=%f." % self.mf
        mapframe = platypus.Frame(doc.leftMargin,\
                                  doc.bottomMargin \
                                  + doc.height*(1-self.mf)\
                                  - self.titleFrameHeight,\
                                  doc.width,\
                                  doc.height*self.mf,\
                                  showBoundary=True,
                                  leftPadding=0,
                                  rightPadding=0,
                                  topPadding=0,
                                  bottomPadding=0)

        # Now work out how big the actual map will be (depends on the
        #   aspect ratio of the area to be mapped).
        self.mapY = mapframe.height        \
                    - mapframe.topPadding \
                    - mapframe.bottomPadding
        self.mapX = self.mapY * self.townguide.map_size_x / self.townguide.map_size_y
        if (self.mapX > \
            (mapframe.width-mapframe.leftPadding-mapframe.rightPadding)):
            self.mapX = mapframe.width \
                        - mapframe.leftPadding \
                        - mapframe.rightPadding
            self.mapY = self.mapX * self.townguide.map_size_y/self.townguide.map_size_x
        print "mapsize = %f, %f" % (self.mapX, self.mapY)

        # how much space is there next to the map - can we fit some columns
        # in there?
        sparew = mapframe.width \
                 + mapframe.leftPadding\
                 + mapframe.rightPadding\
                 - self.mapX

        mapframe.width -= sparew

        overviewPageFrames = [titleframe,mapframe]

        if sparew > self.columnWidth*cm:
            print "adding extra frames next to map"
            colCount = int(sparew / (self.columnWidth*cm))
            colWidth = (sparew)/colCount
            colHeight = doc.height*self.mf   #same as map.

            for colNo in range(colCount):
                leftMargin = doc.leftMargin + \
                             mapframe.width + \
                             mapframe.leftPadding + \
                             mapframe.rightPadding + \
                             colNo*colWidth
                column = platypus.Frame(leftMargin,\
                                        doc.bottomMargin \
                                        +doc.height*(1-self.mf) \
                                        - self.titleFrameHeight,\
                                        colWidth,colHeight,\
                                        showBoundary=True)
                overviewPageFrames.append(column)


        # the columns occupy the bottom half of the page.
        colCount = int(doc.width / (self.columnWidth*cm))
        colWidth = (doc.width)/colCount
        colHeight = doc.height*(1-self.mf) - self.titleFrameHeight

        for colNo in range(colCount):
            leftMargin = doc.leftMargin + colNo*colWidth
            column = platypus.Frame(leftMargin,doc.bottomMargin,\
                                    colWidth,colHeight,\
                                    showBoundary=True)
            overviewPageFrames.append(column)

        #########################################
        # Set up the Detail Map Page Template #
        #########################################
        
        # mapframe spans whole page and goes to half way down the page
        print "self.mf=%f." % self.mf
        # Note, we are using a square map, so doc.width = map.height
        detailmapframe = platypus.Frame(doc.leftMargin,\
                                        doc.bottomMargin \
                                        + doc.height-doc.width\
                                        - self.titleFrameHeight,\
                                        doc.width,\
                                        doc.width,\
                                        showBoundary=True,
                                        leftPadding=0,
                                        rightPadding=0,
                                        topPadding=0,
                                        bottomPadding=0)

        detailPageFrames = [titleframe,detailmapframe]


        # the columns occupy the bottom of the page.
        # again it is a square map, of height=width.
        colCount = int(doc.width / (self.columnWidth*cm))
        colWidth = (doc.width)/colCount
        colHeight = doc.height-doc.width - self.titleFrameHeight

        for colNo in range(colCount):
            leftMargin = doc.leftMargin + colNo*colWidth
            column = platypus.Frame(leftMargin,doc.bottomMargin,\
                                    colWidth,colHeight,\
                                    showBoundary=True)
            detailPageFrames.append(column)




        ################################################################    
        # Set up the overflow pages - just the title frame and columns.#
        ################################################################
        overflowPageFrames = []
        colHeight = doc.height 
        for colNo in range(colCount):
            leftMargin = doc.leftMargin + colNo*colWidth
            column = platypus.Frame(leftMargin,doc.bottomMargin,\
                                    colWidth,colHeight,\
                                    showBoundary=True)
            overflowPageFrames.append(column)
        


        templates = [platypus.PageTemplate(frames=frontPageFrames,\
                                           id="frontpage",
                                           onPage = self.decoratePage),\
                     platypus.PageTemplate(frames=infoPageFrames,\
                                           id="infopage",
                                           onPage = self.decoratePage),\
                     platypus.PageTemplate(frames=overviewPageFrames,\
                                           id="overviewpage",
                                           onPage = self.decoratePage),\
                     platypus.PageTemplate(frames=detailPageFrames,\
                                           id="detailpage",
                                           onPage = self.decoratePage),\
                     platypus.PageTemplate(frames=overflowPageFrames,\
                                           id="overflowpage",
                                           onPage = self.decoratePage)\
                     ]
        doc.addPageTemplates(templates)
        ##############################################################
        #          Now Add the Content                               #
        ##############################################################
        
        style = self.styles["Normal"]
        Story = []

        # Title Page
        Story.append(platypus.Paragraph(self.townguide.title,self.styles["Title"]))
        Story.append(platypus.FrameBreak())
        # im = Image("%s/%s" % (self.townguide.preferences_list['imagePath'],"Openstreetmap_logo.png"))
        im = Image("%s/%s" % (self.townguide.preferences_list['imagePath'],"zoo.png"))
        im.hAlign = 'CENTER'
        style.alignment=styles.TA_CENTER
        Story.append(KeepInFrame(doc.width,doc.height*lf,
                                 [im,
                                  platypus.Paragraph(\
                                      "Produced from OpenStreetMap Data",
                                      style)
                                  ]))
        style.alignment=styles.TA_LEFT
        Story.append(platypus.NextPageTemplate("infopage"))
        Story.append(platypus.PageBreak())

        # Info Page
        Story.append(platypus.Paragraph("Information",self.styles["Title"]))
        Story.append(platypus.FrameBreak())
        Story.append(platypus.Paragraph("Map Data",\
                                        self.styles["Heading2"]))
        Story.append(platypus.Paragraph("The map data used to produce this book"\
                                        " was provided by the OpenStreetMap"\
                                        " project (http://www.openstreetmap.org)."\
                                        ,\
                                        self.styles["Normal"]))
        Story.append(platypus.Paragraph(\
            "OpenStreetMap data is provided freely by volunteers.",
            self.styles["Normal"]))
        Story.append(platypus.Paragraph(\
            "When you identify errors or omissions,"\
            " please report them at http://www.openstreetbugs.org"\
            " or join OpenStreetMap and edit the map yourself!"
            , self.styles["Normal"]))

        Story.append(platypus.Paragraph("Output Generation",\
                                        self.styles["Heading2"]))
        Story.append(\
            platypus.Paragraph(\
                " This PDF output was produced using the TownGuide"\
                " bookRenderer module (http://townguide.webhop.net)."\
                ,\
                self.styles["Normal"]))
        Story.append(\
            platypus.Paragraph(\
                " The map images included in the PDF output was generated "\
                " by mapnik (http://www.mapnik.org)."\
                ,\
                self.styles["Normal"]))

        Story.append(platypus.NextPageTemplate("overviewpage"))
        Story.append(platypus.PageBreak())

        ###############################################################
        # Render the overview map, and add it to the page

        Story.append(platypus.Paragraph("Overview Map",self.styles["Title"]))
        Story.append(platypus.FrameBreak())


        self.townguide.oscale =  1000. *  self.townguide.map_size_x / self.mapX / 2
        self.townguide.drawOverviewMap(self.townguide.outdir,addFeatures=True)

        im = Image("%s/%s" % (self.townguide.outdir,"overview.png"),
                   width=self.mapX, height=self.mapY)
        im.hAlign = 'CENTER'
        Story.append(im)
        # Once we have rendered the map image, we need to go to the next frame.
        Story.append(platypus.FrameBreak())
        Story.append(platypus.NextPageTemplate("overflowpage"))

        ################################################################
        # render the streets in aphabetical order
        if self.townguide.preferences_list['streetIndex'].lower()=='true':
            style.fontName = "Times-Bold"
            Story.append(platypus.Paragraph("Street Index",style))
            style.fontName = "Times-Roman"
            streets = self.townguide.streetIndex.keys()
            streets.sort()
            for street in streets:
                p = Paragraph("%s (%s)" \
                              % (street,self.townguide.streetIndex[street]),style)
                Story.append(p)


        if self.townguide.preferences_list['featureList'].lower()=='true':
            #Do not do a frame break if this is the first frame.
            if self.townguide.preferences_list['streetIndex'].lower()=='true':
                Story.append(platypus.FrameBreak())
            style.fontName = "Times-Bold"
            Story.append(platypus.Paragraph("Points of Interest",style))
            style.fontName = "Times-Roman"
            featurelist = self.townguide.amenities.keys()
            #print self.townguide.amenities
            featurelist.sort()
            featureNo = 1
            for feature in featurelist:
                style.fontName = "Times-Bold"
                Story.append(platypus.Paragraph(feature,style))
                style.fontName = "Times-Roman"
                for rec in self.townguide.amenities[feature]:
                    #print rec
                    lbl = self.townguide.cellLabel(rec[0],rec[1])
                    name = rec[2][1]
                    p = Paragraph("%d: %s (%s)" % (featureNo,name,lbl),style)
                    Story.append(p)
                    featureNo+=1




        if self.townguide.preferences_list['debug'].lower()=='true': 
            # This adds some padding to test the overflow page function.
            for n in range(100):
                p = Paragraph("Para %d - switch off debug mode to remove!!" %\
                              n,style)
                Story.append(p)



        #################################################################
        # Now Add the detail map pages

        for x in range(self.townguide.map_size_x):
            for y in range(self.townguide.map_size_y):
                Story.append(platypus.NextPageTemplate("detailpage"))
                Story.append(platypus.PageBreak())
                Story.append(platypus.NextPageTemplate("overflowpage"))
                Story.append(\
                    platypus.Paragraph("%s" % self.townguide.cellLabel(x,y),
                                       self.styles["Title"]))
                Story.append(platypus.FrameBreak())

                fname = self.townguide.drawTile(x,y)
                im = Image(fname,
                           width=doc.width, height=doc.width)
                im.hAlign = 'CENTER'
                Story.append(im)
                #Story.append(\
                #    platypus.Paragraph("Map goes here",
                #                       self.styles["Title"]))
        

        

        # This line is important - it actually generates the PDF file.
        doc.build(Story)   




    def decoratePage(self,canvas,doc):
        print "decoratePage"
        PAGE_HEIGHT=self.pagesize[1]; PAGE_WIDTH=self.pagesize[0]
        canvas.saveState()
        canvas.setFillColorRGB(0.9,0.9,0.9)
        canvas.rect(5, 5, PAGE_WIDTH-10, PAGE_HEIGHT-10,fill=1)
        canvas.restoreState()
        canvas.saveState()
        canvas.setFont('Times-Bold',16)
        canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-(doc.topMargin/2), self.townguide.title)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(doc.leftMargin, (doc.bottomMargin/2), "Page %s" \
                          % doc.page)
        revStr = "$Rev: 9 $"
        revStr = revStr.split(':')[1]
        revStr = revStr.split('$')[0]
        canvas.drawRightString(doc.leftMargin+doc.width, (doc.bottomMargin/2),
                               "Output Produced by townguide posterRenderer "\
                               "Version %s.       Map data (c) OpenStreetMap and "\
                               "contributors, CC-BY-SA" % revStr)
        canvas.restoreState()

