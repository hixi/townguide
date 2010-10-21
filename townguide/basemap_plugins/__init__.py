"""
mapOverlay_plugins.__init__
All this does is import all of the overlays in the directory.
This is set manually - I might eventually make it clever enough to 
search the directory automatically.
GJ
"""
from mapOverlayBase import mapOverlayBase
from gridOverlay import gridOverlay
from poiOverlay import poiOverlay
from clusterOverlay import clusterOverlay
from gpxOverlay import gpxOverlay

