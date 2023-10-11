odoo.define('fleet_traccar_tracking.FormRenderer', function (require) {
    "use strict";

    var viewRegistry = require('web.view_registry');
    var FormRenderer = require('web.FormRenderer');
    var FormView = require('web.FormView');

    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    
    var TraccarFormRenderer = FormRenderer.extend({
        cssLibs: [
            '/fleet_traccar_tracking/static/src/js/lib/ol-7.1.0/ol.css',
            '/fleet_traccar_tracking/static/src/css/ol_style.css',
        ],
        jsLibs: [
            '/fleet_traccar_tracking/static/src/js/lib/ol-7.1.0/ol.js',
        ],

        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.olmap = null;
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {               
                self.init_olmap();
            });
        },

        _renderView: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.init_olmap();
            })
        },

        on_attach_callback: function () {
            this._super(...arguments);
            var self = this;            
            self.init_olmap();
        },

        init_olmap: function () {            
            var self = this;
            var olmap_div = self.$el.find("#o_traccar_map_view").get(0);
            var olmap = self.load_olmap();
            if (self.olmap) {
                self.olmap.updateSize();
                olmap.setTarget(olmap_div);
                if (self.olmap.values_.target.getAttribute('show_route_trip') == 'true') {
                    self.addRoutePoints();
                }
                if (self.olmap.values_.target.getAttribute('show_current_position') == 'true') {
                    self.addCurrentPosition();
                }
                
            }
        },

        load_olmap: function(){
            var self = this;
            if (!self.olmap) {
                self.olmap = new ol.Map({
                    layers: [
                        new ol.layer.Tile({
                            source: new ol.source.OSM(),
                        }),
                    ],
                    view: new ol.View({
                        center: ol.proj.fromLonLat([0, 0]),
                        zoom: 4,
                    }),
                });
                
                if (self.olmap){
                    self.addLayerVector();
                    self.addLayerpopup();
                }
            }                        
            return self.olmap
        },

        addLayerVector: function(){
            var self = this;        
            if (!cancelIdleCallback.vectorSource) {
                self.vectorSource = new ol.source.Vector();
            }
            if (!self.vectorLayer) {
                self.vectorLayer = new ol.layer.Vector({
                    source: self.vectorSource,
                    name: 'vectorSource',
                    style: new ol.style.Style({
                        fill: new ol.style.Fill({
                            color: 'rgb(255 235 59 / 62%)',
                        }),
                        stroke: new ol.style.Stroke({
                            color: '#ffc107',
                            width: 2,
                        }),
                        image: new ol.style.Circle({
                            radius: 7,
                            fill: new ol.style.Fill({
                                color: '#ffc107',
                            }),
                        }),
                    }),
                });
                self.olmap.addLayer(self.vectorLayer);
            }
        },

        addLayerpopup: function(){
            var self = this;
            var target = self.$el.find('#popup').get(0);
            if (target){
                $(target).removeClass('d-none');
                var popup = new ol.Overlay({
                    element: target,
                    autoPan: true,
                    autoPanAnimation: {
                        duration: 250
                    }
                });
                self.olmap.addOverlay(popup);
                self.olmap.on('pointermove', function (evt) {
                    if (evt.dragging) {
                        return;
                    }
                    if (self.olmap.forEachFeatureAtPixel != undefined ){
                        var feature = self.olmap.forEachFeatureAtPixel(evt.pixel, function (feat, layer) {
                            return feat;
                        });
                        if (feature && feature.get('type') == 'Point') {
                            var coordinate = evt.coordinate;
                            target.innerHTML = feature.get('desc');
                            popup.setPosition(coordinate);
                        }
                        else {
                            popup.setPosition(undefined);                    
                        }
                    }                
                });
            }
        },

        addRoutePoints: function(){
            var self = this;
            self.vectorSource.clear();            
            if (self.state.data.src_latitude && self.state.data.src_longitude) {
                var data = self.state.data;
                var source = {
                    long: data.src_longitude,
                    lat: data.src_latitude,
                    coords: data.src_longitude + ',' + data.src_latitude
                };
                var destination = {
                    long: data.dst_longitude,
                    lat: data.dst_latitude,
                    coords: data.dst_longitude + ',' + data.dst_latitude
                };
    
                var url_osrm_route = '//router.project-osrm.org/route/v1/driving/';
                var url = `${url_osrm_route}${source.coords};${destination.coords}`;
    
                fetch(url).then(function (response) {
                    return response.json();
                }).then(function (json) {                    
                    self.vectorSource.addFeature(self.addMarker(source));
                    self.vectorSource.addFeature(self.addMarker(destination));
                    if(json.code == 'Ok') {
                        self.vectorSource.addFeature(self.addPolyline(json));  
                        self.olmap.getView().fit(self.vectorSource.getExtent(), self.olmap.getSize(), { duration: 100, maxZoom: 6 });
                    }                
                });
            }   
            self.olmap.updateSize();         
        },

        addMarker: function(coords) {
            var self = this;
            var iconStyle = new ol.style.Style({
                image: new ol.style.Icon({
                    scale: .2,
                    crossOrigin: 'anonymous',
                    src: "/fleet_traccar_tracking/static/src/img/marker.png",
                    opacity: 1,
                })
            });
            var desc = '<pre><span style="font-weight: bold;">Waypoint Details</span>' + '<br>' + 'Latitude : ' + coords.lat + '<br>Longitude: ' + coords.long + '</pre>';
            var marker = new ol.Feature({
              geometry: new ol.geom.Point(ol.proj.fromLonLat([coords.long, coords.lat])),
              desc: desc,
              type: 'Point',
            });
            marker.setStyle(iconStyle);
            return marker
        },

        addPolyline: function(json){
            var self = this;
            var routeStyle = {
                route: new ol.style.Style({
                  stroke: new ol.style.Stroke({
                    width: 4, color: [40, 40, 40, 0.8]
                  })
                })
            };
            var geometry = json.routes[0].geometry;
            var format = new ol.format.Polyline({
                factor: 1e5
            }).readGeometry(geometry, {
                dataProjection: 'EPSG:4326',
                featureProjection: 'EPSG:3857',
            });
            
            var polyline = new ol.Feature({
                type: 'route',
                geometry: format
            });
            polyline.setStyle(routeStyle.route);
            return polyline;
        },

        addCurrentPosition: function(){
            var self = this;
            self.vectorSource.clear();
            if (self.state.data.latitude && self.state.data.longitude) {
                var data = self.state.data;
    
                var iconStyle = new ol.style.Style({
                    image: new ol.style.Icon({
                        scale: .2,
                        crossOrigin: 'anonymous',
                        src: "/fleet_traccar_tracking/static/src/img/marker.png",
                        opacity: 1,
                    })
                });
                
                var marker = new ol.Feature({
                  geometry: new ol.geom.Point(ol.proj.fromLonLat([data.longitude, data.latitude])),
                  type: 'Position',
                });
    
                marker.setStyle(iconStyle);
                
                self.vectorSource.addFeature(marker);
                self.olmap.getView().fit(self.vectorSource.getExtent(), { duration: 100, maxZoom: 6 });
            }   
            self.olmap.updateSize();     
        },

    });

    var TraccarFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Renderer: TraccarFormRenderer,
        }),
    });

    viewRegistry.add('traccar_map_form', TraccarFormView);
    return TraccarFormView;
});