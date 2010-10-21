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
#    Copyright Graham Jones 2009
#
#
#

import os

def get_townguide_path():
    package_path, filename =  os.path.split(os.path.abspath(__file__))
    return package_path

# def get_unifont_path():
#     package_path = get_townguide_path()
#     font_path = os.path.join(package_path, 'fonts', 'unifont.ttf')
#     return font_path

# def get_unifont_path():
#     package_path = get_townguide_path()
#     font_path = os.path.join(package_path, 'fonts', 'DroidSansFallback.ttf')
#     return font_path

def get_font_path():
    package_path = get_townguide_path()
    font_path = os.path.join(package_path, 'fonts', 'DroidSans.ttf')
    return font_path

def get_unifont_path():
    package_path = get_townguide_path()
    font_path = os.path.join(package_path, 'fonts', 'osaka.unicode.ttf')
    return font_path


from reportlab.lib import pagesizes
page_sizes = ['letter',
               'A6',
               'A5',
               'A4',
               'A3',
               'A2',
               'A1',
               'A0']

pagesizes_dict = {
    'letter': pagesizes.letter,
    'A6': pagesizes.A6,
    'A5': pagesizes.A5,
    'A4': pagesizes.A4,
    'A3': pagesizes.A3,
    'A2': pagesizes.A2,
    'A1': pagesizes.A1,
    'A0': pagesizes.A0
}









DEFAULT_PREFERENCES = {
    'outdir':'.',
    'datadir':'.',
    'mapfile':'/var/www/townguide/mapStyles/osm-mapnik2.xml',
    'pagesize': 'A4',
    'description': 'No Description Provided',
    'mapvfrac': '80',
    'dpi':'100',
    'tilesize': '1000',
    'clusters': 'false',
    'bottomMargin': '30',
    'topMargin': '72',
    'leftMargin': '10',
    'rightMargin': '10',
    'titleFrameHeight': '0',
    'columnWidth': '5',
    'streetIndex': 'True',
    'featureList': 'True',
    'xapi': 'True',
    'oscale': '10',
    'withThumbnail':'True',
    'debug': 'False',
    'dbname': 'mapnik',
    'uname': 'mapnik',
    'maxmapsize': '15',
    'features': "Banking:amenity='bank'|'atm',"\
    "Shopping:shop='mall'|'supermarket'|'convenience'|'alcohol'|'baker'"
}



test_options = {
    'title':'Example Poster Test',
    'origin': '54.6466,-1.2619',
    'dpi': '300',
    'mapzize': '3,3',
    'format': 'poster',
    'pagesize': 'A4',
    'markersize':'12',
    'mapvfrac': '75',
    'columnWidth': '4.0',
    'streetIndex': 'true',
    'clusters': 'false',
    'outdir': './rendered_maps/',
    'download': 'false',
    'datadir': './townguide/fonts',
    'mapfile': './styles/osm.xml',
    'detailsize': '5',
    'tilesize': '1000',
    'oscale': '10',
    'debug': 'True',
    'dbname': 'mapnik',
    'uname': 'mapnik',
    'features': "Banking:amenity='bank'|'atm',"\
    "Shopping:shop='mall'|'supermarket'|'convenience'|'alcohol'|'baker'"
}

example_poster = {
    'title':'Example Poster Test',
    'origin': '54.6466,-1.2619',
    'dpi': '300',
    'mapzize': '3,3',
    'format': 'poster',
    'pagesize': 'A4',
    'mapvfrac': '75',
    'columnWidth': '4.0',
    'streetIndex': 'true',
    'outdir': './rendered_maps/',
    'download': 'false',
    'datadir': './townguide/fonts',
    'mapfile': './styles/osm.xml',
    'detailsize': '5',
    'tilesize': '1000',
    'oscale': '10',
    'debug': 'True',
    'dbname': 'mapnik',
    'uname': 'mapnik',
    'features': "Banking:amenity='bank'|'atm',"\
    "Shopping:shop='mall'|'supermarket'|'convenience'|'alcohol'|'baker'"
}

example_book = {
    'title':'Example Poster Test',
    'origin': '54.6466,-1.2619',
    'dpi': '300',
    'mapzize': '3,3',
    'format': 'book',
    'pagesize': 'A4',
    'mapvfrac': '75',
    'columnWidth': '4.0',
    'streetIndex': 'true',
    'outdir': './rendered_maps/',
    'download': 'false',
    'datadir': './townguide/fonts',
    'mapfile': './styles/osm.xml',
    'detailsize': '5',
    'tilesize': '1000',
    'oscale': '10',
    'debug': 'True',
    'dbname': 'mapnik',
    'uname': 'mapnik',
    'features': "Banking:amenity='bank'|'atm',"\
    "Shopping:shop='mall'|'supermarket'|'convenience'|'alcohol'|'baker'"
}

example_options = {
    'debug': 'False',
    'origin': '54.6466,-1.2619',
    'mapzize': '3,3',
    'tilesize': '1000',
    'oscale': '10',
    'markersize':'12',
    'datadir': '/home/disk2/www/townguide',
    'mapfile': '/home/disk2/graham/ntmisc/townguide/osm.xml',
    'outdir': '.',
    'uname': 'graham',
    'dbname': 'mapnik',
    'download': 'False',
    'xapi': 'True',
    'features': "Banking:amenity='bank'|'atm',"\
    "Shopping:shop='mall'|'supermarket'|'convenience'|'alcohol'|'baker'"
}


