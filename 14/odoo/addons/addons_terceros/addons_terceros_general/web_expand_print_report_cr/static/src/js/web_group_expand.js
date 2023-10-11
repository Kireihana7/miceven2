odoo.define("web_expand_print_report_cr.web_group_expand", function(require) {
    "use strict";

    var qweb = require("web.core").qweb;
    var rpc = require('web.rpc');
    var session  = require('web.session');
    const framework = require('web.framework');
    var DataExport = require('web.DataExport');

    require("web.ListController").include({
        start: function() {
            this.$expandGroupButtons = $(qweb.render("Expand.Buttons"));
            this.$reportButtons = $(qweb.render("PdfExcel.ReportButtons"));
            
            this.$expandGroupButtons
                .find("#oe_group_by_expand")
                .on("click", this.expandAllGroups.bind(this));
            this.$expandGroupButtons
                .find("#oe_group_by_collapse")
                .on("click", this.collapseAllGroups.bind(this));
            
            this.$reportButtons.find("#button_export_pdf")
            .on("click", this.export_to_excel.bind(this,'pdf'));
            
	        this.$reportButtons
	            .find("#button_export_excel")
	            .on("click", this.export_to_excel.bind(this,'excel'));
            
            return this._super.apply(this, arguments);
        },
        
        on_attach_callback: function () {
        	this._super.apply(this, arguments);
        	this.$expandGroupButtons.toggleClass("d-none", !this.renderer.isGrouped);
        	console.log("thid expand----",this.$expandGroupButtons)
        	console.log("Called00000000",this,this.$el.find('.o_cp_bottom_right'))
        	this.$el.find('.o_cp_buttons .o_list_buttons').append(this.$reportButtons)
        	this.$el.find('.o_cp_buttons .o_list_buttons').append(this.$expandGroupButtons)
        },
        
        _update: function () {
        	var self = this;
            return this._super.apply(this, arguments).then(function(){
            	self.$expandGroupButtons.toggleClass("d-none", !self.renderer.isGrouped);
            })
            
        },

        expandAllGroups: function() {
            // We expand layer by layer. So first we need to find the highest
            // layer that's not already fully expanded.
            var layer = this.renderer.state.data;
            while (layer.length) {
                var closed = layer.filter(function(group) {
                    return !group.isOpen;
                });
                if (closed.length) {
                    // This layer is not completely expanded, expand it
                    this._toggleGroups(closed);
                    break;
                }
                // This layer is completely expanded, move to the next
                layer = _.flatten(
                    layer.map(function(group) {
                        return group.data;
                    }),
                    true
                );
            }
        },

        collapseAllGroups: function() {
            // We collapse layer by layer. So first we need to find the deepest
            // layer that's not already fully collapsed.
            var layer = this.renderer.state.data.filter(function(group) {
                return group.isOpen;
            });
            while (layer.length) {
                var next = _.flatten(
                    layer.map(function(group) {
                        return group.data;
                    }),
                    true
                ).filter(function(group) {
                    return group.isOpen;
                });
                if (!next.length) {
                    // Next layer is fully collapsed, so collapse this one
                    this._toggleGroups(layer);
                    break;
                }
                layer = next;
            }
        },

        _toggleGroups: function(groups) {
            var self = this;
            var defs = groups.map(function(group) {
                return self.model.toggleGroup(group.id);
            });
            $.when(...defs).then(
                this.update.bind(this, {}, {keepSelection: true, reload: false})
            );
        },
        
        
        export_to_excel: function(export_type) {
        	
            var self = this
            var export_type = export_type
            var view = this.getParent()
    		
            // Find Header Element
            var header_eles =  $('.o_list_view > div > table > thead')
            
            var header_name_list = []
            $.each(header_eles,function(){
                var $header_ele = $(this)
                var header_td_elements = $header_ele.find('th')
                $.each(header_td_elements,function(){
                		var $header_td = $(this)
                        var text = $header_td.text().trim() || ""
                        var data_id = $header_td.attr('data-name')
                		header_name_list.push({'header_name': text.trim(), 'header_data_id': data_id})
                });
            });
            
            //Find Data Element
            var data_eles = $('.o_list_view > div > table > tbody > tr:not(.o_add_record_row)')
            		
            var export_data = []
            $.each(data_eles,function(){
                var data = []
                var $data_ele = $(this)
                var is_analysis = false
                
                var is_header_group  = $(this).hasClass('o_group_header') ? true : false;
                if ($data_ele.text().trim()){

                	var extra_td = 0
                    var group_th_eles = $data_ele.find('th')
            		
                    $.each(group_th_eles,function(){
                        var $group_th_ele = $(this)
                        var text = $group_th_ele.text().trim() || ""
                        var is_analysis = true
                        var padding_left = $(this).hasClass('o_group_name') ? $(this).children().css('padding-left') : '0px';
                        
                        if(text) {
                        	if($group_th_ele.attr('colspan') && parseInt($group_th_ele.attr('colspan')) > 1) {
                        		data.push({'padding-left' : padding_left, 'group_row' : is_header_group, 'data': text, 'bold': true,'colspan' : $group_th_ele.attr('colspan')})
                            }
                        	else {
                        		data.push({'padding-left' : padding_left, 'group_row' : is_header_group,'data': text, 'bold': true,'colspan' : 1})
                        	}
                        }
                    });
                	
                	
                    var data_td_eles = $data_ele.find('td')
            		
                    $.each(data_td_eles,function(){
                        var $data_td_ele = $(this)
                        var text = $data_td_ele.text().trim() || ""
                        if($data_td_ele.hasClass('o_list_record_selector')) {
                        	data.push({'data': "",'colspan':1,'group_row' : false,})
                        }
                        else if ($data_td_ele && $data_td_ele[0].classList.contains('oe_number') && !$data_td_ele[0].classList.contains('oe_list_field_float_time')){
                            var text = text.replace('%', '')
                            var text = formats.parse_value(text, { type:"string" });
                            
                            if($data_td_ele.attr('colspan') && parseInt($data_td_ele.attr('colspan')) > 1) {
                        		data.push({'group_row' : is_header_group,'data': text || "", 'number': true,'colspan' : $group_th_ele.attr('colspan')})
                            }
                        	else {
                        		data.push({'group_row' : is_header_group,'data': text || "", 'number': true,'colspan' : 1})
                        	}
                        }
                        else{
                        	if($data_td_ele.attr('colspan') && parseInt($data_td_ele.attr('colspan')) > 1) {
                        		data.push({'group_row' : is_header_group,'data': text,'colspan' : $data_td_ele.attr('colspan')})
                        	}
                        	else {
                        		data.push({'group_row' : is_header_group,'data': text,'colspan' : 1})
                        	}
                        }
                    });
                    
                    var data_length = 0
                	_.each(data,function(dt){
                		data_length += parseInt(dt.colspan)
                	})
                	
                	if(data && header_name_list.length > data_length) {
                		var rows_to_add = header_name_list.length - data_length
        				for(var il=0; il < rows_to_add; il++) {
                			data.push({'group_row' : is_header_group,'data': ""})
                		}
                	}
                    
                    export_data.push(data)
                }
            });
            
            //Find Footer Element
            
            var footer_eles = $('.o_list_view > div > table > tfoot > tr')
            $.each(footer_eles,function(){
                var data = []
                var $footer_ele = $(this)
                var footer_td_eles = $footer_ele.find('td')
                $.each(footer_td_eles,function(){
                    var $footer_td_ele = $(this)
                    var text = $footer_td_ele.text().trim() || ""
                    if ($footer_td_ele && $footer_td_ele[0].classList.contains('oe_number')){
                        var text = formats.parse_value(text, { type:"float" });
                        data.push({'data': text || "", 'bold': true, 'number': true})
                    }
                    else{
                        data.push({'data': text, 'bold': true})
                    }
                });
                export_data.push(data)
            });
            
            //Export to excel
            framework.blockUI();
            if (export_type === 'excel'){
                 session.get_file({
                     url: '/web/export/excel_export',
                     data: {data: JSON.stringify({
                            model : self.modelName,
                            headers : header_name_list,
                            rows : export_data,
                     })},
                     complete: $.unblockUI,
                     error : (error) => self.call('crash_manager','rpc_error',error),
                 });
             }
             else{
                
            	 rpc.query({
            		 model : 'res.users',
            		 method: 'read',
            		 args : [session.uid,["company_id"]],
            	 }).then(function(res){
            		 rpc.query({
                		 model : 'res.company',
                		 method: 'read',
                		 args : [odoo.session_info.user_context.allowed_company_ids[0],["name"]]
                	 }).then(function(result){
                		debugger; return session.get_file({
                             url: '/pdf/reports',
                             data: {data: JSON.stringify({
	                               uid: session.uid,
	                               model : self.modelName,
	                               headers : header_name_list,
	                               rows : export_data,
	                               company_name: result[0].id,
	                               res_ids : self.renderer.state.res_ids,
	                        })},
                             complete: framework.unblockUI,
                             error: (error) => self.call('crash_manager', 'rpc_error', error),
                         });
                	 });
            	 });
             }
        },
    });

    require("web.ListRenderer").include({
        updateState: function() {
            var res = this._super.apply(this, arguments);
            $("nav.oe_group_by_expand_buttons").toggleClass(
                "o_hidden",
                !this.isGrouped
            );
            return res;
        },
    });
});
