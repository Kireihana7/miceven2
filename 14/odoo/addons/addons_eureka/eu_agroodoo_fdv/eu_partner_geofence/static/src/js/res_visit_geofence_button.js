odoo.define('eu_partner_geofence.res_visit_geofence_button_controller', function (require) {
    "use strict";

    require('web.dom_ready');
    const core = require('web.core');
    const _t = core._t;
    const rpc = require('web.rpc');
    var framework = require('web.framework');
    const FormController = require('web.FormController');
    const MyAttendancesPrototype = require('hr_attendance.my_attendances').prototype;
    const MyAttendances = require('hr_attendance.my_attendances');
    const GeofenceDrawing = require('hr_attendance_geofence.GeofenceDrawing').prototype;

    const MyAttendancesInclude = MyAttendances.include({
        checkIsInside: function(prototype=null){
            const self = prototype ?? this;
            let insidePolygon = false;
            let insideGeofences = []
            if(self.olmap){
                for (let i = 0; i < self.geofence.length; i++) {
                    let path = self.geofence[i].overlay_paths;
                    let value = JSON.parse(path);
                    if (Object.keys(value).length > 0) {                                                                    
                        let coords = ol.proj.fromLonLat([self.longitude,self.latitude]);
                        let features = new ol.format.GeoJSON().readFeatures(value);                        
                        let geometry = features[0].getGeometry();
                        let insidePolygon = geometry.intersectsCoordinate(coords);
                        if (insidePolygon === true) {
                            insideGeofences.push(self.geofence[i].id);
                        }
                    }
                }
                if (insideGeofences.length > 0){
                    let position = {
                        latitude: self.longitude,
                        longitude: self.latitude,
                    }
                    if (self.is_partner_geofence) {
                        return true;
                    }
                    self._manual_attendance(position, insideGeofences);
                }else{
                    framework.unblockUI();
                    self.do_notify(false, _t("You haven't entered any of the geofence zones."));
                }
            }
        },
        _initMapWithoutView: async function (prototype=null) {
            const self = prototype ?? this;
            if (window.location.protocol == 'https:'){
                const options = {
                    enableHighAccuracy: true,
                    maximumAge: 30000,
                    timeout: 27000
                };
                if (navigator.geolocation) {
                    return new Promise(function (resolve, reject) {
                        navigator.geolocation.getCurrentPosition(resolve, reject, options);
                    })
                }else {
                    self.geolocation = false;
                }
            }
            else{
                framework.unblockUI();
                self.do_notify(false, _t("GEOLOCATION API MAY ONLY WORKS WITH HTTPS CONNECTIONS."));
            } 
        }
    });

    const FormControllerInclude = FormController.include({
        _onButtonClicked: function (e) {
            const self = this;
            const _super = this._super.bind(this);
            const data = self.renderer.state.data;
            if (e.data.attrs.name === 'eu_custom_button_visitando_geofence') {
                framework.blockUI();
                function successCallback(position, prototype) {
                    var self = prototype;
                    self.latitude = position.coords.latitude;
                    self.longitude = position.coords.longitude;
                    if(!self.olmap){
                        var olmap_div = self.$('.gmap_kisok_view').get(0);
                        $(olmap_div).css({
                            width: '425px !important',
                            height: '200px !important'
                        });                          
                        var vectorSource = new ol.source.Vector({}); 
                        self.olmap = new ol.Map({                            
                            layers: [
                                new ol.layer.Tile({
                                    source: new ol.source.OSM(),
                                }),                                                            
                                new ol.layer.Vector({
                                    source: vectorSource
                                })
                            ],
                            loadTilesWhileInteracting: true,
                            target: olmap_div,
                            view: new ol.View({
                                center: [self.latitude, self.longitude],
                                zoom: 2,
                            }),
                        });
                    }
                    self.def_geolocation.resolve();
                }

                function errorCallback(err, prototype) {
                    var self = prototype;
                    switch(err.code) {
                        case err.PERMISSION_DENIED:
                        console.log("The request for geolocation was refused by the user.");
                        break;
                        case err.POSITION_UNAVAILABLE:
                            console.log("There is no information about the location available.");
                        break;
                        case err.TIMEOUT:
                            console.log("The request for the user's location was unsuccessful.");
                        break;
                        case err.UNKNOWN_ERROR:
                            console.log("An unidentified error has occurred.");
                        break;
                    }
                    self.def_geolocation.resolve();
                }

                let isInside = false;
                MyAttendancesPrototype.geofence_empty = false;

                rpc.query({
                    model: 'res.visit',
                    method: 'get_partner_geofence',
                    args: [{}, e.data.record.data.partner_id.res_id],
                }).then((result) => {
                    MyAttendancesPrototype.geofence = result;
                    if (MyAttendancesPrototype.geofence && MyAttendancesPrototype.geofence.length === 0) {
                        framework.unblockUI();
                        MyAttendancesPrototype.geofence_empty = true;
                        self.do_notify(false, _t("The location or employee are not included in the Geofence List."));
                    }
                });
                
                MyAttendancesPrototype._super = self._super;
                MyAttendancesPrototype.$el = self.$el;
                MyAttendancesPrototype.do_notify = self.do_notify;          
                MyAttendancesPrototype.def_geolocation = $.Deferred();
                MyAttendancesPrototype.is_partner_geofence = true;
                MyAttendancesPrototype._initMapWithoutView(MyAttendancesPrototype)
                .then((result) => {
                    if (!MyAttendancesPrototype.geofence_empty) {
                        successCallback(result, MyAttendancesPrototype);
                        isInside = MyAttendancesPrototype.checkIsInside(MyAttendancesPrototype);
                        if (isInside) {
                            rpc.query({
                                model: 'res.visit',
                                method: 'action_set_status',
                                args: [{}, {
                                    "status": "visitando",
                                    "visit_id": e.data.record.res_id
                                }],
                            }).then(() => {
                                framework.unblockUI();
                                _super.apply(this, arguments);
                                return;
                            })
                        }
                        framework.unblockUI();
                    }
                })
                .catch((err) => {
                    if (!MyAttendancesPrototype.geofence_empty) {
                        framework.unblockUI();
                        errorCallback(err, MyAttendancesPrototype);
                    }
                });
            } else if (e.data.attrs.name === 'eu_custom_button_auto_geofence') {
                if (
                    data.partner_latitude 
                    && data.partner_longitude
                    && !data.geofence_loaction_id
                ) { 
                    GeofenceDrawing._super = self._super;
                    GeofenceDrawing.$el = self.$el;
                    GeofenceDrawing.attrs = {};
                    GeofenceDrawing.attrs.name = 'overlay_paths';
                    GeofenceDrawing._init_olmap();
                    GeofenceDrawing._make_area(data.partner_latitude, data.partner_longitude, 150);
                    var getFeatures = GeofenceDrawing.vectorSource.getFeatures();
                    var _newValue = new ol.format.GeoJSON().writeFeatures(getFeatures);
                    GeofenceDrawing.value = _newValue;
                    if (!data.user_id) {
                        self.do_notify(false, _t("Debe agregar un comercial para crear el Geocerca."));
                        return;
                    }
                    rpc.query({
                        model: 'hr.attendance.geofence',
                        method: 'auto_create',
                        args: [{}, {
                            'name': data.name,
                            'partner_id': data.id,
                            'overlay_paths': _newValue
                        }, data.user_id.res_id],
                    }).then((message) => {
                        self.do_notify(false, _t(message));
                        _super.apply(this, arguments);
                    });
                }
            } else if (e.data.attrs.name === 'eu_custom_button_geolocalize'){
                const geolocalizeCallbackThen = (position) => {
                    rpc.query({
                        model: 'res.partner',
                        method: 'set_current_position',
                        args: [{}, data.id, position.coords.latitude, position.coords.longitude]
                    }).then(() => {
                        framework.unblockUI();
                        self.do_notify(false, _t('Se actualizaron las coordenadas del contacto.'));
                        _super.apply(this, arguments);
                    });
                }

                const geolocalizeCallbackCatch = (err) => {
                    framework.unblockUI();
                    self.do_notify(false, _t('Ha ocurrido un error actualizando las coordenadas del contacto.'));
                    _super.apply(this, arguments);
                    console.log(err);
                }

                const options = {
                    enableHighAccuracy: true,
                    maximumAge: 30000,
                    timeout: 27000
                };

                if (window.location.protocol == 'https:'){
                    framework.blockUI();
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(geolocalizeCallbackThen, geolocalizeCallbackCatch, options);
                    }
                } else {
                    framework.unblockUI();
                    self.do_notify(false, _t("GEOLOCATION API MAY ONLY WORKS WITH HTTPS CONNECTIONS."));
                }
            } else {
                _super.apply(this, arguments);
            }
        }
    })
});