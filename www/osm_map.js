/* coding: utf-8
 *
 * maposmatic, the web front-end of the MapOSMatic city map generation system
 * Copyright (C) 2009 David Decotigny
 * Copyright (C) 2009 Frédéric Lehobey
 * Copyright (C) 2009 David Mentré
 * Copyright (C) 2009 Maxime Petazzoni
 * Copyright (C) 2009 Thomas Petazzoni
 * Copyright (C) 2009 Gaël Utard
 * Copyright (C) 2009 Étienne Loks
 * Copyright (C) 2009 Graham Jones - converted for townguide.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * See the file COPYING for details.
 */

/* OSM slippy map management. */

var map = null;
var update_lock = 0;
var epsg_display_projection = new OpenLayers.Projection('EPSG:4326');
var epsg_projection = new OpenLayers.Projection('EPSG:900913');
var vecLayer = null

function getOriginLon() { return document.getElementById('lon'); }
function getOriginLat() { return document.getElementById('lat'); }
function getNx() { return document.getElementById('nx'); }
function getNy() { return document.getElementById('ny'); }

/** Map Zoom/Move events callback: update form fields on zoom action. */
function updateForm()
{
    if (update_lock)
      return;

    var bounds = map.getExtent();

    var topleft = new OpenLayers.LonLat(bounds.left, bounds.top);
    topleft = topleft.transform(epsg_projection, epsg_display_projection);

    var bottomright = new OpenLayers.LonLat(bounds.right, bounds.bottom);
    bottomright = bottomright.transform(epsg_projection, epsg_display_projection);

    getOriginLat().value = bottomright.lat.toFixed(4);
    getOriginLon().value = topleft.lon.toFixed(4);
    updateMap();  /* To update the shaded select area */
}

/* Update the map on form field modification. */
function updateMap()
{
    var origin = new OpenLayers.LonLat(getOriginLon().value,
				       getOriginLat().value);
    origin.transform(epsg_display_projection, epsg_projection);
    var nx = getNx().value;
    var ny = getNy().value;
    var bounds = new OpenLayers.Bounds(origin.lon,
				       origin.lat,
				       origin.lon+1000*nx,
				       origin.lat+1000*ny);
    update_lock = 1;
    /*map.setCenter(origin,12);*/
    /*map.zoomToExtent(bounds);*/
    update_lock = 0;

    var pointList = [];
    var newPoint = new OpenLayers.Geometry.Point(origin.lon,origin.lat);
    pointList.push(newPoint);
    var newPoint = 
	new OpenLayers.Geometry.Point(origin.lon,
				      origin.lat+1000*ny);
    pointList.push(newPoint);
    var newPoint = 
	new OpenLayers.Geometry.Point(origin.lon+1000*nx,
				      origin.lat+1000*ny);
    pointList.push(newPoint);
    var newPoint = 
	new OpenLayers.Geometry.Point(origin.lon+1000*nx,
				      origin.lat);
    pointList.push(newPoint);
    pointList.push(pointList[0]);

    var linearRing = new OpenLayers.Geometry.LinearRing(pointList);
    var polyFeature = 
	new OpenLayers.Feature.Vector(
				      new OpenLayers.Geometry.Polygon([linearRing]));
    vecLayer.destroyFeatures();
    vecLayer.addFeatures([polyFeature]);
}

function zoomMap() 
{
    var origin = new OpenLayers.LonLat(getOriginLon().value,
				       getOriginLat().value);
    origin.transform(epsg_display_projection, epsg_projection);
    var nx = parseInt(getNx().value);
    var ny = parseInt(getNy().value);
    var bounds = new OpenLayers.Bounds(origin.lon,
				       origin.lat,
				       origin.lon+1000*nx,
				       origin.lat+1000*ny);
    map.zoomToExtent(bounds);
    map.zoomToScale(10000000.);

}
/* Main initialisation function. Must be called before the map is manipulated. */
function init()
{
    /*alert("init");*/
    map = new OpenLayers.Map ('map', {
        controls:[new OpenLayers.Control.Navigation(),
                  new OpenLayers.Control.PanZoomBar(),
                  new OpenLayers.Control.Attribution()],
        maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
        numZoomLevels: 18,
        maxResolution: 156543.0399,
        projection: epsg_projection,
        displayProjection: epsg_display_projection
    } );

    layerTilesMapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
    map.addLayer(layerTilesMapnik);

    vecLayer = new OpenLayers.Layer.Vector("SelectArea");
    map.addLayer(vecLayer);

    /*map.events.register('zoomend', map, updateForm);*/
    map.events.register('moveend', map, updateForm);
    updateMap();
    zoomMap();
    /*map.zoomto(5);*/
}

