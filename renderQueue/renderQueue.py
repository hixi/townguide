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
import psycopg2 as psycopg


class renderQueue:
    def __init__(self,daemon,init):
        self.dbname = "townguide"
        self.uname  = "graham"

        if (init):
            self.initialiseDB()

        self.queueLoop()

    def initialiseDB(self):
        print "Initialising the database";
        
            
        connection = psycopg.connect('dbname=%s' % self.dbname,\
                                     'user=%s' % self.uname)
        mark = connection.cursor()

        sqlstr = "drop table queue;"
        # We use this try/pass to avoid a crash if the table does not exist.
        try:
            mark.execute(sqlstr)
        except:
            pass
        

        sqlstr = "create table queue ("\
                 "jobNo int,"\
                 "status int,"\
                 "title char(255),"\
                 "subData date,"\
                 "finDate date,"\
                 "xml char(255)"\
                 ");"
        print sqlstr
        mark.execute(sqlstr)
        
        
        sqlstr = "select * from queue;"
        mark.execute(sqlstr)
        records = mark.fetchall()
        
        print len(records)
        for rec in records:
            print rec


    def queueLoop(self):
        print "queueLoop"


if __name__ == "__main__":
    from optparse import OptionParser

    usage = "Usage %prog [options]"
    version = "SVN Revision $Rev$"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-d", "--daemon", action="store_true",dest="daemon",
                      help="Run as a daemon")
    parser.add_option("-i", "--init", action="store_true",dest="init",
                      help="Initialise the database")
    parser.set_defaults(
        daemon=False,
        init=False)
    (options,args)=parser.parse_args()
    
    print
    print "%s %s" % ("%prog",version)
    print
    

    rq = renderQueue(options.daemon,options.init)

