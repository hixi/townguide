import basemapBase

class mapnikRenderer(basemapBase.basemapBase):

    def render(self,fname):
        tx=10
        ty=10
        minx = self.townguide.c0.x \
            + self.townguide.preferences_list['tilesize'] * tx
        miny = self.townguide.c0.y \
            + self.townguide.preferences_list['tilesize'] * ty
        
        if HAS_MAPNIK2:
            bbox = mapnik.Box2d(minx,
                                miny,
                                minx+self.townguide.preferences_list['tilesize'],
                                miny+self.townguide.preferences_list['tilesize'])
        else:
            bbox = mapnik.Envelope(minx,
                                   miny,
                                   minx+self.townguide.preferences_list['tilesize'],
                                   miny+self.townguide.preferences_list['tilesize'])
                
        # First draw the basic map using mapnik.
        fname = "%s/image_%02d_%02d.png" % (self.townguide.preferences_list['outdir'],tx,ty)
        
        imgx = int(self.townguide.preferences_list['tilesize'] / \
                       self.townguide.preferences_list['oscale'])
        imgy = int(self.preferences_list['tilesize'] / \
                       self.townguide.preferences_list['oscale'])
        self.drawTile_bbox(bbox,imgx,imgy,fname)


    def drawTile_bbox(self,bbox,imgx,imgy,fname):
        """Call Mapnik to draw a map image for data in
        bounding box bbox.  The image size is imgx by imgy pixels, and
        the output filename is fname.

        29sep2009  GJ  ORIGINAL VERSION, based on generate_image.py
        06jan2010  GJ  Renamed to drawTile_bbox from drawTile
        """
        mapfile = str(self.preferences_list['mapfile'])
        map_uri = str(fname)
        print ("mapfile=%s" % mapfile)

        # png image
        m = mapnik.Map(imgx,imgy)
        mapnik.load_map(m,mapfile)
        m.zoom_to_box(bbox)
        im = mapnik.Image(imgx,imgy)

        if HAS_MAPNIK2:
            # We apply the scale factor to the map
            print 'using scale factors from mapnik2'
            scale_factor = float( self.preferences_list['dpi'] ) / 72
            print "Scale factor is: ", scale_factor, "================="
            mapnik.render(m, im, scale_factor)
        else:
            print 'NOT using scale_factors'
            mapnik.render(m, im)
            
        view = im.view(0,0,imgx,imgy) # x,y,width,height
        view.save(map_uri,'png')

        # Adding support for svg image
        #print "Creating svg image"
        #import cairo
        #svg_map_uri = ''.join([fname, ".svg"])
        #print svg_map_uri
        #svg_file = open(svg_map_uri, 'w')
        #surface = cairo.SVGSurface(svg_file.name, m.width,m.height)
        #mapnik.render(m, surface)
        #surface.finish()

        #print "Creating PDF surface image"
        #pdf_map_uri = ''.join([fname, ".pdf"])
        #print pdf_map_uri
        #pdf_file = open(pdf_map_uri, 'w')
        #surface = cairo.PDFSurface(pdf_file.name, m.width,m.height)
        #mapnik.render(m, surface)
        #surface.finish()

            
