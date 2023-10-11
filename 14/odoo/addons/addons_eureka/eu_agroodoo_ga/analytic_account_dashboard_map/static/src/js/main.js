odoo.define('analytic_account_dashboard_map.Dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var AbstractController = require('web.AbstractController');
    var AbstractModel = require('web.AbstractModel');
    var AbstractRenderer = require('web.AbstractRenderer');
    var AbstractView = require('web.AbstractView');
    var viewRegistry = require('web.view_registry');
    var core = require('web.core');
    var _t = core._t;
    var self = this;
    var QWeb = core.qweb;
    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var rpc = require('web.rpc');
    var myChart = null;
    var myChart2 = null;
    var map_regions_bar = null;
    var map_country_bar = null;
    var start = null;
    var end = null;
    var t_save_imagen = _t("Save as imagen");
    var t_reset = _t("Reset");
    var t_sales_in = _t("Farms in ");
    var t_from = _t("From ");
    var t_to = _t(" to ");
    var tooltip = {
            trigger: 'item',
            showDelay: 0,
            transitionDuration: 0.2,
            formatter: function (params) {
                var value = (params.value + '').split('.');
                value = value[0].replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, '$1,');
                return params.seriesName + '<br/>' + params.name + ': ' + value;
            }
        };
    var toolbox = {};
    var emphasis = {
             itemStyle:{
                shadowColor: 'rgba(0, 0, 0, 0.9)',
                shadowBlur: 10,
                areaColor: '#9ffea2'
             },
             label: {
                show: true
             }
        };
    var show_data = {
            show:true,
            color: '#ec6633',
            formatter: function (params) {
                var value = (params.value + '').split('.');
                value = value[0].replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, '$1,');
                return params.name + ': ' + value;
            }
       };
    var AnalyticAccountDashboardMap = AbstractAction.extend({
        cssLibs: [
            '/analytic_account_dashboard_map/static/src/css/estilos.css',
            '/analytic_account_dashboard_map/static/src/css/daterangepicker.css'
         ],
        jsLibs: [
            '/analytic_account_dashboard_map/static/lib/echarts.min.js',
            '/analytic_account_dashboard_map/static/lib/moment.min.js',
            '/analytic_account_dashboard_map/static/lib/daterangepicker.min.js',
        ],
        template: 'AnalyticAccountDashboardMap',
        events: {
            'change #cmbRegions': function(e) {
                    e.stopPropagation();
                    var $target = $(e.target);
                    var value = $target.val();
                    this.load_map_region(value, $("#cmbRegiones option:selected").text());
            },
            'change #cmbCountry': function(e) {
                    e.stopPropagation();
                    var $target = $(e.target);
                    var value = $target.val();
                    this.load_map_country(value, $("#cmbCountry option:selected").text());
            },
            'change #range': function(e) {
                    this.load_data_country();
                    this.load_data_region();

            },
            'change #cmbLandDivision': function(e) {
                    this.load_data_country();
                    this.load_data_region();
            },
            'change #cmbMeasures': function(e) {
                    this.load_data_country();
                    this.load_data_region();
            },
            'change #show_data_country': function(e) {
                    this.load_data_country();
            },
            'change #show_data_region': function(e) {
                    this.load_data_region();
            },
            'change #cmbFarmer': function(e) {
                    this.load_data_country();
                    this.load_data_region();
            },
        },

        start: function() {
            console.log("START FUNCTION");

        },
        init: function () {
            this._super.apply(this, arguments);
            this.ruining = true;
            t_save_imagen = _t("Save as imagen");
            t_reset = _t("Reset");
            t_sales_in = _t("Farms in ");
            t_from = _t("From ");
            t_to = _t(" to ");
            toolbox = {
               show: true,
               left: 'left',
               top: 'top',
               feature: {
                    restore: {
                        iconStyle:{
                            borderColor: "rgba(255, 0, 0, 1)",
                            borderWidth: 2
                        },
                        title: t_reset,
                        emphasis: {
                          iconStyle: {
                            borderColor: "rgba(255, 115, 0, 1)"
                          }
                        }
                    },
                    saveAsImage: {
                        iconStyle:{
                            borderColor: "rgba(255, 0, 0, 1)",
                            borderWidth: 2
                        },
                        title: t_save_imagen,
                        emphasis: {
                          iconStyle: {
                            borderColor: "rgba(255, 115, 0, 1)"
                          }
                        }
                    }
               }
            };
        },
        destroy: function () {
            console.log('destroy');
        },

        renderElement: function (ev) {
            var self = this;
            $.when(this._super()).then(function (ev) {
                start = moment().subtract(29, 'days');
                end = moment();
                myChart = echarts.init(document.getElementById('map1'));
                myChart.showLoading();
                myChart2 = echarts.init(document.getElementById('map2'));
                myChart2.showLoading();

                map_regions_bar = echarts.init(document.getElementById('map_regions_bar'));
                map_country_bar = echarts.init(document.getElementById('map_country_bar'));
                $('#reportrange').daterangepicker({
                    startDate: start,
                    endDate: end,
                    ranges: {
                       'Today': [moment(), moment()],
                       'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                       'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                       'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                       'This Month': [moment().startOf('month'), moment().endOf('month')],
                       'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
                    }
                }, cb);

                $('#reportrange #range').val(start.format('YYYY-MM-DD') + ' - ' + end.format('YYYY-MM-DD'));
                rpc.query({
                    model: "res.country",
                    method: "get_url_maps",
                    args: [''],
                }).then(function (result) {
                        $('#cmbCountry').html('');
                        if(result instanceof Array) {
                            if(result.length > 0) {
                                result.forEach(function(valor, clave) {
                                    $('#cmbCountry').append('<option value="'+valor.url+'">'+valor.country+'</option>');
                                });                            
                            }                            
                        }
                        self.load_map_country($("#cmbCountry").val(), $("#cmbCountry option:selected").text());
                        self.load_map_region('/analytic_account_dashboard_map/static/src/maps/World.json', 'World');
                });
                rpc.query({
                    model: "account.analytic.account",
                    method: "get_all_farmers",
                    args: [''],
                }).then(function (result) {
                    console.log('Farmers:');
                    console.log(result);
                    $('#cmbFarmer').html('<option value="all">'+_t("All")+'</option>');
                    if(result instanceof Array) {
                        if(result.length > 0) {
                            result.forEach(function(valor, clave) {
                                $('#cmbFarmer').append('<option value="'+valor.id+'">'+valor.name+'</option>');
                            });                    
                        }
                    }
                });
            });
        },

        load_data_country: function(){
            console.log('Ejecutando función "load_data_country"');

            var self = this;
            myChart.showLoading();
            var drp = $('#reportrange').data('daterangepicker');
            var from = drp.startDate.format('YYYY-MM-DD');
            var to = drp.endDate.format('YYYY-MM-DD');
            var land_division = $("#cmbLandDivision option:selected").val();
            var measures = $("#cmbMeasures option:selected").val();
            var country_url = $("#cmbCountry option:selected").val();
            var country_name = $("#cmbCountry option:selected").text();
            var country_code = getIdParameter(country_url);
            var farmer = $("#cmbFarmer option:selected").val();
            console.log('country_code: ' + country_code);

            // Quantity of elements:
            let land_division_text = $("#cmbLandDivision option:selected").html();
            if( land_division_text == '' ) {
                $("#cmbLandDivision option:first").html();
            }
            let text = `Cantidad de ${land_division_text}`;
            $("#cmbMeasures option").eq(1).html(text);

            rpc.query({
                model: "account.analytic.account",
                method: "load_data_country",
                args: [
                    [0],
                    from, // 0
                    to, // 1
                    land_division, // 2
                    measures, // 3
                    country_code, // 4
                    farmer // 5
                ],
            }).then(function (result) {
                console.log('Result:');
                console.log(result);                
                var datos = [];
                var values = [];
                var countrys = [];
                if(result instanceof Array) {
                    if(result.length > 0) {
                        result.forEach(function(valor, clave) {

                            // if(valor.parcel_count == null) {
                            //     valor.parcel_count = 0;
                            // }
                            // let value_txt = `Farms: ${valor.farm_count} - Parcels: ${valor.parcel_count}`;

                            let country_state = valor.country_state;
                            let chart_value = 0;

                            if( measures == 1 ) { // <------- Quantity of elements
                                switch(land_division) {
                                    case 'farm':
                                        chart_value = valor.farm_count;
                                        break;
                                    case 'parcel':
                                        chart_value = valor.parcel_count;
                                        break;
                                    case 'tablon':
                                        chart_value = valor.tablon_count;
                                        break;                                                              
                                }
                            } else if ( measures == 0 ) { // <------- Analytic Entries
                                switch(land_division) {
                                    case 'farm':
                                        chart_value = valor.amount_total_farm;
                                        break;
                                    case 'parcel':
                                        chart_value = valor.amount_total_parcel;
                                        break;
                                    case 'tablon':
                                        chart_value = valor.amount_total_tablon;
                                        break;                                                              
                                }                                
                            }

                            if( chart_value == null ) {
                                chart_value = 0;
                            }
                            // console.log('chart_value: ' + chart_value + ' - ' + 'land_division: ' + land_division);

                            if($("#show_data_country").is(':checked')){
                                datos.push({name: country_state, value: chart_value, label:show_data});
                            }else{
                                datos.push({name: country_state, value: chart_value});
                            }
                            countrys.push(country_state);
                            values.push(chart_value);
                        });                    
                    }
                }

                if(values.length>0){
                    var max = Math.max(...values);
                    var min = Math.min(...values);
                    var optionCountry = {
                        title: {
                            text: t_sales_in+country_name+' ('+$("#cmbLandDivision option:selected").text()+' - '+$("#cmbMeasures option:selected").text()+')',
                            subtext: t_from+from+t_to+to,
                            left: 'right',
                            subtextStyle: {
                                color: '#000'
                            }
                        },
                        tooltip: tooltip,
                        toolbox: toolbox,
                        visualMap: visualMap(max,min),
                        series: [
                            {
                                name: country_name,
                                type: 'map',
                                roam: true,
                                map: 'Country',
                                selectedMode: 'multiple',
                                data:datos,
                                emphasis: emphasis
                            }
                        ]
                    };
                    myChart.hideLoading();
                    myChart.setOption(optionCountry, true);

                }else{
                    var optionCountry = {
                        title: {
                            text: t_sales_in+country_name+' ('+$("#cmbLandDivision option:selected").text()+' - '+$("#cmbMeasures option:selected").text()+')',
                            subtext: t_from+from+t_to+to,
                            left: 'right',
                            subtextStyle: {
                                color: '#000'
                            }
                        },
                        tooltip: tooltip,
                        toolbox: toolbox,
                        series: [
                            {
                                name: country_name,
                                type: 'map',
                                roam: true,
                                map: 'Country',
                                emphasis: emphasis
                            }
                        ]
                    };
                    myChart.hideLoading();
                    myChart.setOption(optionCountry, true);
                }
                self.render_map_country_bar(values,countrys);
            });
        },

        load_data_region: function(){
            var self = this;
            myChart2.showLoading();
            var drp = $('#reportrange').data('daterangepicker');
            var from = drp.startDate.format('YYYY-MM-DD');
            var to = drp.endDate.format('YYYY-MM-DD');
            var state = $("#cmbLandDivision option:selected").val();
            var measures = $("#cmbMeasures option:selected").val();
            var region = $("#cmbRegions option:selected").text();
            var farmer = $("#cmbFarmer option:selected").val();
            var land_division = $("#cmbLandDivision option:selected").val();
            rpc.query({
                model: "account.analytic.account",
                method: "load_data_region",
                args: [
                    '',
                    from,
                    to,
                    state,
                    measures,
                    region,
                    farmer
                ],
            }).then(function (result) {
                var datos = [];
                var values = [];
                var regions = [];
                if(result instanceof Array) {
                    if(result.length > 0) {
                        result.forEach(function(valor, clave) {

                            switch(land_division) {
                                case 'farm':
                                    chart_value = valor.farm_count;
                                case 'parcel':
                                    chart_value = valor.parcel_count;
                                case 'tablon':
                                    chart_value = valor.tablon_count;                                                              
                            }


                            if($("#show_data_region").is(':checked')){
                                datos.push({name: valor.country, value: chart_value, label: show_data});
                            }else{
                                datos.push({name: valor.country, value: chart_value});
                            }
                            values.push(chart_value);
                            regions.push(valor.country);
                        });                    
                    }
                }
            
                if(values.length>0){
                    var max = Math.max(...values);
                    var min = Math.min(...values);
                    var optionRegion = {
                            title: {
                                text: t_sales_in+region+' ('+$("#cmbLandDivision option:selected").text()+' - '+$("#cmbMeasures option:selected").text()+')',
                                subtext: t_from+from+t_to+to,
                                left: 'right',
                                subtextStyle: {
                                    color: '#000'
                                }
                            },
                            tooltip: tooltip,
                            toolbox: toolbox,
                            visualMap: visualMap(max,min),
                            series: [
                                {
                                    name: region,
                                    type: 'map',
                                    roam: true,
                                    map: 'region',
                                    data: datos,
                                    selectedMode: 'multiple',
                                    emphasis: emphasis
                                }
                            ]
                    };
                    myChart2.hideLoading();
                    myChart2.setOption(optionRegion, true);

                }else{
                    var optionRegion = {
                            title: {
                                text: t_sales_in+region+' ('+$("#cmbLandDivision option:selected").text()+' - '+$("#cmbMeasures option:selected").text()+')',
                                subtext: t_from+from+t_to+to,
                                left: 'right',
                                subtextStyle: {
                                    color: '#000'
                                }
                            },
                            tooltip: tooltip,
                            toolbox: toolbox,
                            series: [
                                {
                                    name: name,
                                    type: 'map',
                                    roam: true,
                                    map: 'region',
                                    emphasis: emphasis
                                }
                            ]
                    };
                    myChart2.hideLoading();
                    myChart2.setOption(optionRegion, true);
                }
                self.render_map_regions_bar(values, regions);
            });
        },

        load_map_country: function (f,name) {
            var self = this;
            myChart.showLoading();
            var drp = $('#reportrange').data('daterangepicker');
            var from = drp.startDate.format('YYYY-MM-DD');
            var to = drp.endDate.format('YYYY-MM-DD');
            $.get(f, function (countryJson) {
                    echarts.registerMap('Country', countryJson);
                    var option = {
                        title: {
                            text: t_sales_in+name+' ('+$("#cmbLandDivision option:selected").text()+' - '+$("#cmbMeasures option:selected").text()+')',
                            subtext: t_from+from+t_to+to,
                            left: 'right',
                            subtextStyle: {
                                color: '#000'
                            }
                        },
                        tooltip: tooltip,
                        toolbox: toolbox,
                        series: [
                            {
                                name: name,
                                type: 'map',
                                roam: true,
                                map: 'Country',
                                emphasis: emphasis
                            }
                        ]
                    };
                    self.load_data_country();
                    myChart.hideLoading();
                    myChart.setOption(option, true);
                });
        },

        load_map_region: function (f,name) {
            var self = this;
            myChart2.showLoading();
            var drp = $('#reportrange').data('daterangepicker');
            var from = drp.startDate.format('YYYY-MM-DD');
            var to = drp.endDate.format('YYYY-MM-DD');
            $.get(f, function (regionJson) {
                    echarts.registerMap('region', regionJson);
                    var option2 = {
                        title: {
                            text: t_sales_in+name+' ('+$("#cmbLandDivision option:selected").text()+' - '+$("#cmbMeasures option:selected").text()+')',
                            subtext: t_from+from+t_to+to,
                            left: 'right',
                            subtextStyle: {
                                color: '#000'
                            }
                        },
                        tooltip: tooltip,
                        toolbox: toolbox,
                        series: [
                            {
                                name: name,
                                type: 'map',
                                roam: true,
                                map: 'region',
                                emphasis: emphasis
                            }
                        ]
                    };
                    self.load_data_region();
                    myChart2.hideLoading();
                    myChart2.setOption(option2, true);
            });
        },

        render_map_country_bar: function (values, country){
            var drp = $('#reportrange').data('daterangepicker');
            var from = drp.startDate.format('YYYY-MM-DD');
            var to = drp.endDate.format('YYYY-MM-DD');
            var state = $("#cmbLandDivision option:selected").val();
            var measures = $("#cmbMeasures option:selected").val();
            var region = $("#cmbRegions option:selected").text();
            var farmer = $("#cmbFarmer option:selected").val();

            var country_name = $("#cmbCountry option:selected").text();
            var optionCountry = {}
            
            console.log('Valores para la función "render_map_country_bar"');
            console.log(values);

            if(values.length>0){
                var max = Math.max(...values);
                var min = Math.min(...values);
                optionCountry = {
                        title: {
                            text: t_sales_in+country_name+' ('+$("#cmbLandDivision option:selected").text()+' - '+$("#cmbMeasures option:selected").text()+')',
                            subtext: t_from+from+t_to+to,
                            left: 'right',
                            subtextStyle: {
                                color: '#000'
                            }
                        },
                        xAxis: {
                                type: 'value',
                                boundaryGap: [0, 0.1],
                                axisLabel: {
                                    show: false,
                                }
                        },
                        yAxis: {
                                type: 'category',
                                axisLabel: {
                                    textStyle: {
                                        color: '#000'
                                    }
                                },
                                data: country
                        },
                        tooltip: tooltip,
                        toolbox: toolbox,
                        visualMap: visualMap(max,min),
                        series: [
                                    {
                                        id: 'bar',
                                        type: 'bar',
                                        tooltip: {
                                            show: false
                                        },
                                        itemStyle: {
                                                width: 3,
                                                shadowColor: 'rgba(0,0,0,0.4)',
                                                shadowBlur: 10,
                                                shadowOffsetY: 10
                                        },
                                        label: {
                                            normal: {
                                                show: true,
                                                position: 'right',
                                                textStyle: {
                                                    color: '#000'
                                                },
                                                formatter: function (params) {
                                                    var value = (params.value + '').split('.');
                                                    value = value[0].replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, '$1,');
                                                    return value;
                                                }
                                            }
                                        },
                                        data: values
                                    }
                        ]
                };
            }else{

            }

            map_country_bar.setOption(optionCountry, true);
        },
        render_map_regions_bar: function (values, regions){
            var drp = $('#reportrange').data('daterangepicker');
            var from = drp.startDate.format('YYYY-MM-DD');
            var to = drp.endDate.format('YYYY-MM-DD');
            var state = $("#cmbLandDivision option:selected").val();
            var measures = $("#cmbMeasures option:selected").val();
            var region = $("#cmbRegions option:selected").text();
            var farmer = $("#cmbFarmer option:selected").val();
            var optionRegion = {};
            if(values.length>0){
                var max = Math.max(...values);
                var min = Math.min(...values);
                optionRegion = {
                            title: {
                                text: t_sales_in+region+' ('+$("#cmbLandDivision option:selected").text()+' - '+$("#cmbMeasures option:selected").text()+')',
                                subtext: t_from+from+t_to+to,
                                left: 'right',
                                subtextStyle: {
                                    color: '#000'
                                }
                            },
                            tooltip: tooltip,
                            toolbox: toolbox,
                            visualMap: visualMap(max,min),
                            xAxis: {
                                type: 'value',
                                boundaryGap: [0, 0.1],
                                axisLabel: {
                                    show: false,
                                }
                            },
                            yAxis: {
                                type: 'category',
                                axisLabel: {
                                    textStyle: {
                                        color: '#000'
                                    }
                                },
                                data: regions
                            },
                            series: [
                                {
                                        id: 'bar',
                                        type: 'bar',
                                        tooltip: {
                                            show: false
                                        },
                                        itemStyle: {
                                                width: 3,
                                                shadowColor: 'rgba(0,0,0,0.4)',
                                                shadowBlur: 10,
                                                shadowOffsetY: 10
                                        },
                                        label: {
                                            normal: {
                                                show: true,
                                                position: 'right',
                                                textStyle: {
                                                    color: '#000'
                                                },
                                                formatter: function (params) {
                                                    var value = (params.value + '').split('.');
                                                    value = value[0].replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, '$1,');
                                                    return value;
                                                }
                                            }
                                        },
                                        data: values
                                    }
                            ]
                    };
            }
            map_regions_bar.setOption(optionRegion, true);
        }

    });


    core.action_registry.add('analytic_account_dashboard_map', AnalyticAccountDashboardMap);

    function cb(start, end){
            var self = this;
            $('#reportrange #range').val(start.format('YYYY-MM-DD') + ' - ' + end.format('YYYY-MM-DD'));
            $('#range').change();
    };

    function getIdParameter(url) {
        var url = url.split('&');
        var sParameterName;
        var i;

        for (i = 0; i < url.length; i++) {
            sParameterName = url[i].split('=');
            if (sParameterName[0] === 'code') {
                return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
            }
        }
    };

    function visualMap(max2,min2){
        return {
                   left: 'right',
                   dimension: 0,
                   min: min2,
                   max: max2,
                   inRange: {
                      color: ['lightskyblue', 'yellow', 'orangered', 'red']
                   },
                   text: [_t('High'), _t('Low')],
                   formatter: function (params) {
                        var value = (params + '').split('.');
                        value = value[0].replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, '$1,');
                        return value;
                   },
                   calculable: true
               };
    };

    return AnalyticAccountDashboardMap;


});
