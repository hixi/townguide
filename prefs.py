#!/usr/bin/python

import sys
import os
from xml.sax import make_parser, handler
import xml
import re
import time

class prefs(handler.ContentHandler):
    """
    A simple class to handle reading and writing preferences to files on disk.
    The preferences are stored as simple key value pairs, and use xml for disk storage.
    Each preference is a separate xml element - attributes are not used.
    There is no heirarchy of preferences - it is a simple list.

    Example usage would be
        pr = prefs()
        preflist=pr.loadPrefs("prefs.xml")
        for p in preflist:
            print "pref",p,preflist[p]

        preflist['newPref']=value

        pr.savePrefs("prefs_out.xml",True)

    You can also call up a Graphical Editor by doing:
        pr.guiEdit()
    Parameters for guiEdit can control how much the user is allowed
    to alter - the default is that they can alter any key or value, and
    can add and delete rows.

    Copyright Graham Jones, September 2009.
    """

    def __init__(self,opt_debug=False,opt_verbose=False):
        """Initialise the Preferences reader/writer - does not actually
        do anything"""
        self.debug = opt_debug
        self.verbose = opt_verbose
        self.inEle = False
        self.inXML = False
        self.eleStr=""
        self.tags={}
        #self.tags=[]

    def getPrefs(self):
        """Returns the dictionary containing the preferences"""
        return self.tags


    def savePrefs(self,filename,overwrite=False):
        """Write the current set of preferences to file 'filename'.
        If overwrite==False it will
        fail if the file already exists, otherwise it will
        overwrite any pre-existing file.
        """
        print "savePrefs: overwrite=",overwrite
        if (overwrite==False) and (os.path.exists(filename)):
            print "Error - File %s already exists." % filename
        else:
            op = open(filename,"w")
            op.write("<xml>\n")
            for tag in self.tags:
                op.write("<%s>%s</%s>\n"%(tag,self.tags[tag],tag))
            op.write("</xml>\n")
            op.close
                     
            return

    def loadPrefs(self, filename):
        """Load a Preferences XML file 'filename' into memory and
        return a dictionary 
        containing the preferences specified in the file"""
        if(not os.path.exists(filename)):
            print "Error - File %s does not exist." % filename
            return
        try:
            parser = make_parser()
            parser.setContentHandler(self)
            parser.parse(filename)
            self.fname = filename
            return self.tags
        except xml.sax._exceptions.SAXParseException:
            print "Error loading %s" % filename

    def loadPrefsFromString(self, xmlStr):
        """Load a Preferences XML string 'xmlStr' into memory and
        return a dictionary 
        containing the preferences specified in the file"""
        try:
            parser = make_parser()
            parser.setContentHandler(self)
            parser.parseString(xmlStr)
            self.fname = filename
            return self.tags
        except xml.sax._exceptions.SAXParseException:
            print "Error loading %s" % filename



    def applyDefaults(self,defs):
        """
        Applys a specified set of default values to the set of preferences.
        If a value in defs is already defined, it is ignored.
        If it is not defined, it is added to the set of preferences with
        the specified default value.
        Returns the updated list of tags and values.
        
        30dec2009  GJ  ORIGINAL VERSION
        """
        for key in defs:
            print "Checking default %s" % key
            if self.tags.get(key) == None:
                print "adding default %s " % key
                self.tags[key]=defs[key]
        return self.tags

    def guiEdit(self,allowAdd=True,
                allowDelete=True,
                allowChangeKeys=True,
                allowChangeValues=True):
        """
        Display a dialog box allowing the user to edit the preferences.
        The parameters (allowAdd, allowDelete etc.) control how much
        the user is allowed to change - the default is everything.
        """
        pg = prefGUI(allowAdd,allowDelete,allowChangeKeys,allowChangeValues)
        pg.guiEdit(self.tags)
        pl = pg.getNewPreflist()
        print "prefGUI exited..."
        print pl

        if (pl!=None):
            self.tags=pl


    def startElement(self, name, attrs):
        """Handle XML elements - called by the xml parser"""
        if (self.debug): print "startElement: name=%s, attr=%s" % (name,attrs)
        if name=="xml":
            if (self.debug): print "start of XML"
            self.inXML=True
        else:
            if (self.debug): print "start of element %s." % name
            self.inEle=True
        

    def characters(self, content):
        """Handle characters read from the XML file - called by the XML parser"""
        if(self.inEle):
            if (self.debug): print "adding %s to current element." % content
            self.eleStr = self.eleStr + content
        else:
            if (self.verbose):
                print "characters - inEle=",self.inEle," content=%s."%content
                print "Warning: we have got characters, but we are not in an element!!!: Ignoring" 

    def endElement(self, name):
        """Called by the XML parser - when an end of element tag is found, it saves
        the preference to the 'self.tags' dictionary.
        """
        if (self.debug): print "endElement - name=%s." % name
        if (self.inEle):
            if (self.debug): print "inEle is true, saving tag %s as %s." % (name,self.eleStr)
            #self.tags.append((name,self.eleStr))
            self.tags[name]=self.eleStr
            self.inEle = False
            self.eleStr=""
            if (self.debug): print self.tags[name]
        elif (self.inXML):
            if (self.debug): print "End of XML found"
        else:
            print "ERROR: we have ended an element, but we are not in an element!!!: Ignoring"             


try:
    import pygtk
    pygtk.require("2.0")
    import gtk

    class prefGUI:
        def __init__(self,allowAdd=True,
                     allowDelete=True,
                     allowChangeKeys=True,
                     allowChangeValues=True):
            print "prefGUI.__init__"

            self.allowAdd=allowAdd
            self.allowDelete=allowDelete
            self.allowChangeKeys=allowChangeKeys
            self.allowChangeValues=allowChangeValues

            self.newPreflist = None
            builder = gtk.Builder()
            builder.add_from_file("prefs.glade")
            builder.connect_signals(self)
            self.window = builder.get_object("prefDialogWindow")
            self.confDelDlg = builder.get_object("confirmDeleteDialog")
            self.loadFileChooserDlg = builder.get_object("prefFileChooserDialog")

            b = builder.get_object("addButton")
            if self.allowAdd==False:
                b.hide()
            else:
                b.show()
            b = builder.get_object("deleteButton")
            if self.allowDelete==False:
                b.hide()
            else:
                b.show()


            self.store = gtk.ListStore(str,str)
            self.treeview = builder.get_object("treeview1")
            self.treeview.set_model(self.store)

            # create the TreeViewColumn to display the data (Keys First)
            keycell = gtk.CellRendererText()
            if self.allowChangeKeys:
                keycell.set_property('editable',True)
                keycell.connect('edited',self.on_edited_event,(self.store,0))
            else:
                keycell.set_property('editable',False)
            tvcolumn = gtk.TreeViewColumn('Key')
            tvcolumn.pack_start(keycell, True)
            tvcolumn.add_attribute(keycell, 'text', 0)
            tvcolumn.set_sort_column_id(0)
            self.treeview.append_column(tvcolumn)

            # now values
            valcell = gtk.CellRendererText()
            if self.allowChangeValues:
                valcell.set_property('editable',True)
                valcell.connect('edited',self.on_edited_event,(self.store,1))
            else:
                valcell.set_property('editable',False)
            tvcolumn = gtk.TreeViewColumn('Value')
            tvcolumn.pack_start(valcell, True)
            tvcolumn.add_attribute(valcell, 'text', 1)
            tvcolumn.set_sort_column_id(1)
            self.treeview.append_column(tvcolumn)

            self.treeview.set_search_column(0)


        def guiEdit(self,preflist):
            # Populate the list store object from the preference list supplied
            # to init.
            for p in preflist:
                print "pref",p,preflist[p]
                self.store.append([p,preflist[p]])

            self.window.show()
            self.window.run()

        def getNewPreflist(self):
            return self.newPreflist


        def on_edited_event(self,cell,path,new_text,data):
            store,colno=data
            print "on_edited_event - colno=",colno," text=",new_text
            store[path][colno]=new_text
            return

        def on_okButton_clicked(self,widget,data=None):
            print "on_okButton_clicked"
            self.window.hide()
            it = self.store.get_iter_first()
            if (it!=None):
                self.newPreflist = {}


                while (it!=None):
                    key = self.store.get_value(it,0)
                    value = self.store.get_value(it,1)
                    print key,":",value
                    self.newPreflist[key]=value
                    it = self.store.iter_next(it)
            else:
                self.newPreflist = None

        def on_cancelButton_clicked(self,widget,data=None):
            print "on_cancelButton_clicked"
            self.newPrefList = None
            self.window.hide()

        def on_addButton_clicked(self,widget,data=None):
            print "on_addButton_clicked"
            it =self.store.append()
            ts = self.treeview.get_selection()
            ts.select_iter(it)

        def on_deleteButton_clicked(self,widget,data=None):
            print "on_deleteButton_clicked"
            ts = self.treeview.get_selection()
            model,it = ts.get_selected()
            if (it!=None):
                response=self.confDelDlg.run()
                self.confDelDlg.hide()
                if (response==gtk.RESPONSE_YES):
                    print "deleting..."
                    del model[it]
                else:
                    print "ok - leaving it alone"
            else:
                print "no row selected - ignoring delete" 

except:
    class prefGUI:
        def __init__(self,allowAdd=True,
                     allowDelete=True,
                     allowChangeKeys=True,
                     allowChangeValues=True):
            print "prefGUI.__init__"
        def guiEdit(self,preflist):
            pass

        def getNewPreflist(self):
            pass

    

"""
Main program called if this python script file is executed directly rather than used as
a module
"""
if __name__ == "__main__":
    from optparse import OptionParser

    usage = "Usage %prog [options] filename"
    version = "0.1"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-i", "--interactive", action="store_true", dest="interactive",
                      help="Show the preferences editor to interactively edit the specified preferences file.")
    #parser.add_option("-f", "--file", dest="outfile",
    #                  help="filename to use for output",
    #                  metavar="FILE")
    parser.add_option("-v", "--verbose", action="store_true",dest="verbose",
                      help="Include verbose output")
    parser.add_option("-d", "--debug", action="store_true",dest="debug",
                      help="Include debug output")
    parser.set_defaults(
        interactive=False,
        debug=False,
        verbose=False)
    (options,args)=parser.parse_args()
    
    if (options.debug):
        options.verbose = True
        print "options   = %s" % options
        print "arguments = %s" % args

    if options.interactive:
        if len(args)<1:
            print "Error: You must supply at least one GPX file to analyse.\n"
            sys.exit(-1)
        else:
            pr = prefs()
            preflist = pr.loadPrefs(args[0])
            pr.guiEdit(True,True,True,True)
            pr.savePrefs(args[0],True)
    else:  #   must be test mode
        pr = prefs()
        preflist=pr.loadPrefs("prefs.xml")
        #preflist = prefs.getPrefs()
        for p in preflist:
            print "pref",p,preflist[p]

        preflist['newPref']='newPref Value'
        
        pr.savePrefs("prefs_out.xml",True)
            
        print "Edit only values"
        pr.guiEdit(False,False,False,True)
        
        print "Edit keys and values"
        pr.guiEdit(False,False,True,True)

        print "add and delete rows"
        pr.guiEdit(True,True,True,True)

        preflist = pr.getPrefs()
        for p in preflist:
            print "pref",p,preflist[p]

    








