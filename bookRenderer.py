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

#from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
#from reportlab.lib.styles import getSampleStyleSheet
#from reportlab.rl_config import defaultPageSize
#from reportlab.lib.units import inch
#from reportlab.lib import pagesizes

#PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
#styles = getSampleStyleSheet()


class bookRenderer(): 
    def __init__(self,tg):
        print "bookRenderer.init()"
        self.tg = tg

#        pageSizeDict = {
#            'letter': pagesizes.letter,
#            'A6': pagesizes.A6,
#            'A5': pagesizes.A5,
#            'A4': pagesizes.A4,
#            'A3': pagesizes.A3,
#            'A2': pagesizes.A2,
#            'A1': pagesizes.A1,
#            'A0': pagesizes.A0
#            }
#        self.pagesize = pageSizeDict.get(self.tg.pl['pagesize'])

#        if self.pagesize == None:
#            print ("ERROR - Pagesize %s unrecognised - Using A4 instead\n" \
#                   % ps_str)
#            self.pagesize = pagesizes.A4

            


    def renderPDF(self):
        print "Rendering PDF File using pdfLatex"
        outpath = "%s/%s.tex" % (self.tg.outdir,self.tg.outdir)
        f = open(outpath,"w")
        f.write("\\documentclass{book}\n")
        f.write("\\usepackage{graphicx}\n")
        f.write("\\renewcommand{\\topfraction}{0.9}")
        f.write("\\renewcommand{\\bottomfraction}{0.8}")
        f.write("\\renewcommand{\\floatpagefraction}{0.7}")
        f.write("\\renewcommand{\\textfraction}{0.07}")
        f.write("\\begin{document}\n")
        f.write("\\parindent 0pt\n")
        f.write("\\parskip 12pt\n")
        f.write("\\title{%s}\n" % self.tg.title)
        f.write("\\author{Graham Jones}")
        f.write("\\maketitle\n")
        f.write("\\tableofcontents\n")

        ############### Introduction #########################
        f.write("\\chapter{Introduction}\n")
        f.write("This document contains provided by OpenStreetMap \n")
        f.write("(http://www.openstreetmap.org).\n\n")
        f.write("OpenStreetMap data is provided freely by volunteers.  When you identify\n")
        f.write("errors or omissions in the data, please report them at\n")
        f.write("OpenStreetBugs (http://www.openstreetbugs.org)\n")
        f.write("or join OpenStreetMap and improve the data yourself!\n\n")
        f.write("This document was produced by 'TownGuide' (http://code.google.com/p/ntmisc)\n\n")
        f.write("\\copyright Graham Jones, 2009.\n")

        ############### Overview Map Page ######################
        f.write("\\chapter{Overview}\n")
        f.write("\\begin{figure}[h]\n")
        f.write("\\caption{Overview Map}\n")
        f.write("\\includegraphics[width=5cm]{overview.png}\n")
        #f.write("\\includegraphics[width=5cm]{%s/overview.png}\n" % self.tg.outdir)
        f.write("\\end{figure}\n")

        ############### Street Index ###########################
        f.write("\\chapter{Street Index}\n")

        # render the streets in aphabetical order
        streets = self.tg.streetIndex.keys()
        streets.sort()
        f.write("\\begin{table}[h]\n")
        f.write("\\caption{Alphabetical Street Index}\n")
        f.write("\\begin{tabular}{|l|l|}\\hline\n")
        f.write("\\textbf{\\textsc{Street Name}}&\\textbf{\\textsc{Grid Ref}}\\\\ \\hline\n")
        for street in streets:
            f.write("%s&%s\\\\ \\hline\n" % (street,self.tg.streetIndex[street]))
        f.write("\\end{tabular}\n\\end{table}\n")

        



        ############### Features ###############################
        f.write("\\chapter{Features}\n")
        featurelist = self.tg.amenities.keys()
        print self.tg.amenities
        featurelist.sort()
        for feature in featurelist:
            f.write("\\section{%s}\n" % feature)
            f.write("\\begin{table}[h]\n")
            f.write("\\caption{%s}\n" % feature)
            f.write("\\begin{tabular}{|l|l|}\\hline\n")
            f.write("\\textbf{\\textsc{Name}}&\\textbf{\\textsc{Grid Ref}}\\\\ \\hline\n")
            for rec in self.tg.amenities[feature]:
                print rec
                lbl = self.tg.cellLabel(rec[0],rec[1])
                name = rec[2][1]
                #f.write("%s %s <br>" % (lbl,name))
                f.write("%s&%s\\\\ \\hline\n" % (lbl,name))
            f.write("\\end{tabular}\n\\end{table}\n")
                    


        ############### End of Latex Document ##################
        f.write("\\end{document}\n");

        f.close()

        ############### Run Latex to Create PDF ################
        import subprocess
        command = "cd %s; pdflatex %s.tex" % (self.tg.outdir,self.tg.outdir)
        self.latex_proc = subprocess.Popen(command,shell=True)
        if self.latex_proc!=None:
            #print "latex_proc exists - checking status.."
            self.latex_proc.poll()
            if (self.latex_proc.returncode==None):
                print "latex still alive - waiting"
                finished=False
                while (finished!=True):
                    self.latex_proc.poll()
                    if (self.latex_proc.returncode!=None):
                        print "latex finished."
                        finished = True
            else:
                print "latex already dead - noting to do!"

        ########## Run Latex Again to do Table of Contents to ############
        command = "cd %s; pdflatex %s.tex" % (self.tg.outdir,self.tg.outdir)
        self.latex_proc = subprocess.Popen(command,shell=True)
        if self.latex_proc!=None:
            #print "latex_proc exists - checking status.."
            self.latex_proc.poll()
            if (self.latex_proc.returncode==None):
                print "latex still alive - waiting"
                finished=False
                while (finished!=True):
                    self.latex_proc.poll()
                    if (self.latex_proc.returncode!=None):
                        print "latex finished."
                        finished = True
            else:
                print "latex already dead - noting to do!"



#    def posterPage(self,canvas,doc):
#        canvas.saveState()
#        canvas.setFont('Times-Bold',16)
#        canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, self.tg.title)
#        canvas.setFont('Times-Roman',9)
#        canvas.drawString(inch, 0.75 * inch, "Page / %s" % "parameter")
#        canvas.restoreState()


    def render(self):
        print "bookRenderer.render()"
        self.renderPDF()
#        doc = SimpleDocTemplate("townguide_poster.pdf",pagesize=self.pagesize)
#        Story = [Spacer(1,2*inch)]
#        style = styles["Normal"]

#        im = Image("%s/%s" % (self.tg.outdir,"overview.png"),
#                   width=2*inch, height=2*inch)
#        im.hAlign = 'CENTER'
#        Story.append(im)
#        Story.append(Spacer(1,0.2*inch))

#        bogustext = ("This is Paragraph ")
#        p = Paragraph(bogustext, style)
#        Story.append(p)

        # render the streets in aphabetical order
#        streets = self.tg.streetIndex.keys()
#        streets.sort()
#        for street in streets:
#            print("%s (%s)<br>" % (street,self.tg.streetIndex[street]))
#            p = Paragraph("%s (%s)" % (street,self.tg.streetIndex[street]),style)
#            Story.append(p)


#        doc.build(Story, onFirstPage=self.posterPage)
            
