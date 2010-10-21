#!/usr/bin/python

import townguide
from prefs import prefs
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
    townguide.townguide(preferences)
    
