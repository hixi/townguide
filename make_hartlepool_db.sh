#!/bin/sh
wget http://www.openstreetmap.org/api/0.6/map?bbox=-1.311492919921875,54.60786894786166,-1.110992431640625,54.729378425601766 -O hartlepool.osm

osm2pgsql -d mapnik -s hartlepool.osm

