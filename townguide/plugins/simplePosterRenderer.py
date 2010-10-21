#!/usr/bin/env python
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
#    Copyright Waldemar Quevedo 2010
#

from reportlab.platypus import SimpleDocTemplate, Paragraph, BaseDocTemplate
from reportlab.platypus import Spacer, Image, Frame
from reportlab.platypus import PageTemplate, FrameBreak, NextPageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.lib.units import cm
from townguide.defaults import DEFAULT_PREFERENCES, pagesizes_dict

# Register unicode font 
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from townguide.defaults import get_unifont_path
unifont = TTFont('unifont', get_unifont_path())
pdfmetrics.registerFont(    unifont    )


class simplePosterRenderer( ):
    """
    A townguide plugin for rendering a map in poster mode
    alongside a description of the map
    """

    def __init__(self, townguide):

        self.townguide = townguide
        townguide.preferences.applyDefaults(DEFAULT_PREFERENCES)

        try:
            self.pagesize = pagesizes_dict.get(
                self.townguide.preferences_list['pagesize'])
        except:
            self.pagesize = pagesizes.A4
        (self.page_width, self.page_height) = self.pagesize

        self.stylesheet = getSampleStyleSheet()


    def canvas_callback(self,canvas, document):
        canvas.saveState()
        canvas.drawRightString(document.leftMargin + document.width,
                               (document.bottomMargin / 2),
                               "Map data (c) OpenStreetMap and contributors, CC-BY-SA")
        canvas.restoreState()


    def laterpages_canvas_callback(self,canvas, document):
        canvas.saveState()
        # Draw the Points of Interest title string as well
        canvas.setFont("Helvetica-Bold", 25)
        canvas.drawString(document.leftMargin,
                          self.page_height - self.page_height * 0.09,
                          "Points of Interest"
                          )
        canvas.setFont("Helvetica", 10)
        canvas.drawRightString(document.leftMargin + document.width,
                               (document.bottomMargin / 2),
                               "Map data (c) OpenStreetMap and contributors, CC-BY-SA")
        canvas.restoreState()

    def render(self):
        """
        Townguide plugin render method implemented to create a
        pdf of a map with description in a landscape orientation
        """
        output_file = "%s/%s" % (self.townguide.outdir, "townguide_poster.pdf")
        # document = SimpleDocTemplate(output_file,
        #                              pagesize=(self.page_width, self.page_height))

        document = BaseDocTemplate(output_file,
                                     pagesize=(self.page_width, self.page_height))

        # Title frame for both cases
        # Both layouts
        titleframe_width = document.width
        titleframe_height = 1.4*cm
        titleframe = Frame(
            document.leftMargin,
            document.bottomMargin + document.height - 0.2*cm,
            titleframe_width,
            titleframe_height,                       # 1.4cm
            showBoundary=None,
            leftPadding=0.5*cm,
            rightPadding=0,
            topPadding=0.5*cm,
            bottomPadding= 0*cm,
            )

        # First, determine the layout depending on the size of the map
        map_width    =  float(   self.townguide.preferences_list['map_size_x']  )
        map_height   =  float(   self.townguide.preferences_list['map_size_y']  )
        
        if map_width > map_height:
            # -----------------
            #  Title          |  
            #  .............  | 
            #  ..          .  |
            #  ..          .  |
            #  .............  |
            #  Description    |
            #                 |
            #                 |
            #                 |
            #  ----------------
            
            HORIZONTAL = True
            
            aspect_ratio = map_height / map_width
            mapframe_width = self.page_width * 0.9
            mapframe_height = mapframe_width * aspect_ratio
            
            detailframe_width = self.page_width * 0.7
            detailframe_height = self.page_height * 0.7

            print "-------------------------------"
            print "width: ", document.width
            print "height: ", document.height

            print "page width: ", self.page_width
            print "page height: ", self.page_height
            
            print "mapframe_width", mapframe_width
            print "-------------------------------"
            
            mapframe = Frame(
                1.0*cm,
                self.page_height - document.topMargin \
                    - titleframe_height \
                    - mapframe_height,
                mapframe_width + 0.5*cm,  # document.width,
                mapframe_height + 0.5*cm, # document.height - 5*cm,
                showBoundary=None,
                leftPadding=0,
                rightPadding=0,
                topPadding=0.1*cm,
                bottomPadding=0
                )
            
            detailframe = Frame(
                document.leftMargin,
                self.page_height \
                    - document.topMargin \
                    - titleframe_height \
                    - mapframe_height \
                    - detailframe_height,
                detailframe_width,
                detailframe_height,
                showBoundary=None,
                leftPadding=0,
                rightPadding=0,
                topPadding=0.3*cm,
                bottomPadding=0
                )

        else:
            # -----------------
            #  Title          |  
            #  .............  | 
            #  ..          .  |
            #  ..          .  |
            #  ..          .  |
            #  ..          .  |
            #  ..          .  |
            #  .............  |
            #  Description    |
            #  ----------------
            HORIZONTAL = False
            print "-------------------------------"
            print "width: ", document.width
            print "height: ", document.height

            print "page width: ", self.page_width
            print "page height: ", self.page_height
            print "-------------------------------"

            aspect_ratio = map_width / map_height

            # if height is larger
            # this should be of the same size as the frame
            # mapframe_height = self.page_height * 0.52
            detailframe_width = self.page_width * 0.8 - self.page_width * 0.07 
            detailframe_height = self.page_height * 0.15

            # mapframe_width = self.page_width * 0.5 - self.page_width * 0.05
            # mapframe_height = mapframe_width * aspect_ratio

            mapframe_height = self.page_height * 0.65 - 0.5*cm
            mapframe_width = mapframe_height * aspect_ratio

            # document.leftMargin,
            # document.bottomMargin,
            mapframe = Frame(
                0.5*cm,
                self.page_height - document.topMargin \
                    - titleframe_height \
                    - mapframe_height,
                mapframe_width + 0.5*cm,  # document.width,
                mapframe_height + 0.5*cm, # document.height - 5*cm,
                showBoundary=None,
                leftPadding=0,
                rightPadding=0,
                topPadding=0.1*cm,
                bottomPadding=0
                )
            
            detailframe = Frame(
                document.leftMargin,
                self.page_height \
                    - document.topMargin \
                    - titleframe_height \
                    - mapframe_height \
                    - detailframe_height,
                detailframe_width,
                detailframe_height,
                showBoundary=None,
                leftPadding=0,
                rightPadding=0,
                topPadding=0.3*cm,
                bottomPadding=0
                )

            # detailframe_width = self.page_width * 0.2
            # detailframe_width = self.page_width \
            #                     - mapframe_width \
            #                     - document.rightMargin \
            #                     - self.page_width * 0.1
            # detailframe_height = self.page_height * 0.5
            # detailframe = Frame(
            #     # document.leftMargin + self.page_width * 0.9,
            #     document.leftMargin + mapframe_width + 0.5*cm,
            #     document.bottomMargin + mapframe_height + 0.5*cm - detailframe_height,
            #     detailframe_width,
            #     detailframe_height,
            #     showBoundary=None,
            #     leftPadding=0,
            #     rightPadding=0,
            #     topPadding=0.3*cm,
            #     bottomPadding=0
            #     )
            
        print "===================================================="
        print "width: ", map_width
        print "height: ", map_height
        print "aspect_ratio: ", aspect_ratio
        print "mapframe_width: ", mapframe_width
        print "mapframe_height: ", mapframe_height
        print "detailframe_height: ", detailframe_height
        print "===================================================="
        
        # FRAMES setup ==============================
        # Frame(x, y, width, height...)
        #             width                    x2,y2
        # |      +---------------------------------+
        # |      | l  top padding                r | h
        # |      | e +-------------------------+ i | e
        # |      | f |                         | g | i
        # |      | t |                         | h | g
        # |      |   |                         | t | h
        # |      | p |                         |   | t
        # |      | a |                         | p |
        # |      | d |                         | a |
        # |      |   |                         | d |
        # |      |   +-------------------------+   |
        # |      |    bottom padding               |
        # |      +---------------------------------+
        # |      (x1,y1) <-- lower left corner

        # first page with the map and information paragraph
        pageframes = [titleframe]
        pageframes.append(mapframe)
        pageframes.append(detailframe)

        # ::: LATER PAGES :::
        # ----------------------------
        #            POIs             |  
        #  ............ ............  |
        #  .          . .          .  |
        #  .          . .          .  |
        #  .          . .          .  |
        #  .          . .          .  |
        #  .          . .          .  |
        #  .          . .          .  |
        #  ............ ............  |
        # ----------------------------
        laterpagesframes = []
        
        columns = 3
        column_width = document.width / columns
        column_height = document.height

        for column in range(columns):
            left_margin = document.leftMargin + column * column_width
            columnframe = Frame(
                left_margin,
                document.bottomMargin,
                column_width,
                column_height,
                showBoundary=None
                )
            laterpagesframes.append(columnframe)

        templates = [PageTemplate(frames=pageframes,
                                  id="first",
                                  onPage=self.canvas_callback),
                     PageTemplate(frames=laterpagesframes,
                                  id="laterPages",
                                  onPage=self.laterpages_canvas_callback)]
        
        document.addPageTemplates(templates)
        # END of frames setup ==============================

        # Story setup ======================================
        story = []

        # TITLE
        s = self.stylesheet['Heading1']
        # s.fontName = "Helvetica-Bold"
        s.fontName = "unifont"
        p = Paragraph(   self.townguide.preferences_list['title'], s)
        story.append(p)
        story.append(FrameBreak())
        story.append(Spacer(1, 0.2*cm))

        # IMAGE
        # TODO: Resolution and scaling.
        # This should be handled by mapnik later on.
        # `oscale` is metres per pixels
        dpi = float (self.townguide.preferences_list['dpi'])
        pixels = mapframe_width * dpi / 72

        oscale = self.townguide.preferences_list['tilesize'] * map_width / pixels
        
        self.townguide.preferences_list['oscale'] =  oscale
        
        # RENDER THE IMAGE
        self.townguide.drawOverviewMap(self.townguide.outdir,
                                       addFeatures=True)
        
        osm_image_name = "%s/%s" % (self.townguide.outdir, "overview.png")
        osm_image = Image( osm_image_name,
                           mapframe_width, mapframe_height )
        story.append(osm_image)
        story.append(FrameBreak())

        # INFORMATION
        s = self.stylesheet['Heading1']
        s.fontName = "Helvetica-Bold"
        p = Paragraph("Information", s)
        story.append(p)

        s = self.stylesheet['Normal']
        s.fontName = "unifont"
        p = Paragraph(self.townguide.preferences_list['description'], s)
        story.append(p)


        # POIS information => if street index is true in the preferences_list
        if self.townguide.preferences_list['streetIndex'].lower() == 'true':
            story.append(NextPageTemplate("laterPages"))
            # FIXME: I don't know why, but a break is needed here
            story.append(FrameBreak())  
            
            # TITLE. Goes into a callback
            # s = self.stylesheet['Normal']
            # s.fontName = "Helvetica-Bold"
            # s.fontSize = 25
            # story.append(Paragraph("Points of Interest", s))
            # story.append(FrameBreak())
            
            # GETTING THE AMENITIES            
            feature_list = self.townguide.amenities.keys()
            feature_list.sort()
            feature_number = 1

            for feature in feature_list:
                story.append(Spacer(1, 0.2*cm))
                s.fontName = "Helvetica-Bold"
                s.fontSize = 15
                story.append(Paragraph(feature, s))
                story.append(Spacer(1, 0.2*cm))

                # Now add the records of that kind of POI
                s.fontName = "unifont"
                s.fontSize = 10
                for record in self.townguide.amenities[feature]:
                    label = self.townguide.cellLabel(record[0], record[1])
                    poi_name = record[2][1]
                    text = "%d:[%s] %s" % (feature_number, label, poi_name)
                    story.append(Paragraph(text, s))
                    feature_number += 1

        document.build(story)
