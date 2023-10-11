odoo.define('aspl_quick_invoice.quick_invoice', function (require) {
"use strict";


	var core = require('web.core');
	var rpc = require('web.rpc');
	var Dialog = require('web.Dialog');
	var session = require('web.session');
	var utils = require('web.utils');
	var field_utils = require('web.field_utils');
	var NotificationManager = require('web.Notification');
	var ListController = require('web.ListController');
    var AbstractAction = require('web.AbstractAction');
	var round_di = utils.round_decimals;
	var QWeb = core.qweb;
	var _t = core._t;

    var DiscountDialog = Dialog.extend({
		events: {
            'submit form': '_onFormSubmit',
            'click .btn-primary': '_onFormSubmit',
        },
        _onFormSubmit: function (ev) {
            if (ev) {
                ev.preventDefault();
            }
            var form = this.$('form')[0];
            var formdata = new FormData(form);
            var data = {};
            for (var field of formdata) {
                data[field[0]] = field[1];
            }
            if (data.selected_line){
                this.trigger_up('discount-submit', data);
                form.reset();
                this.close();
            }else{
                alert("Please selected line into cart!");
            }
            console.log("\n\n trigger up called")
        },
    });

    var PriceDialog = Dialog.extend({
		events: {
            'submit form': '_onFormSubmit',
            'click .btn-primary': '_onFormSubmit',
        },
        _onFormSubmit: function (ev) {
            if (ev) {
                ev.preventDefault();
            }
            var form = this.$('form')[0];
            var formdata = new FormData(form);
            var data = {};
            for (var field of formdata) {
                data[field[0]] = field[1];
            }
            if (data.selected_line){
                this.trigger_up('price-submit', data);
                form.reset();
                this.close();
            }else{
                alert("Please selected line into cart!");
            }
            console.log("\n\n trigger up called")
        },
    });

	var QuickInvoiceAction = AbstractAction.extend({
	    title: core._t('Invoice Order'),
	    template: 'QuickInvoiceAction',
	    events: {
	        'click .open-datetimepicker': '_sale_date_picker',
	        'click .product-delete': '_product_delete',
	        'click .discount-delete': '_discount_delete',
	        'click .cart-row-item': '_cart_line_click',
	        'click .sale-mode-disc-btn':'_numpad_disc_button_click',
	        'click .sale-mode-price-btn':'_numpad_price_button_click',
	        'click .minus':'_qunt_minus_click',
	        'click .plus':'_qunt_plus_click',
	        'click .cart-row-item .cart-content': 'cart_content',
	        'focusout input.product_qty': 'product_qty_out',
	        'focusout input.product_price': 'product_price_out',
	        'focusout input.product_disc': 'product_disc_out',
	        'click .payment_method': 'payment_method_click',
	        'change #price_list': 'change_price_list',
	        'click #state_type': 'state_click',
	        'click .execute': 'create_po',
	        'click .recent_orders': 'recent_orders',
	        'click .td_sale_order': 'td_sale_order',
	        'click .delete-payment-line': 'delete_payment_line',
	        'click .paymentline': 'paymentline_click',
	        'keyup .paymentline .payment-input': 'payment_input',
	        'click .delivery-confirm': 'delivery_confirm',
	        'change #invoice_type':'change_invoice_type',
	        'click #customer_txt':'click_customer_txt',
	        'click .search-product input':'search_product_click',
	        'click #slidemenubtn':'slidemenubtn',
	        'change #multi_company': 'change_multi_company',
	        'change #currency':'_compute_currency',
	    },
	    custom_events: {
        	'discount-submit': '_onSaveDiscount',
        	'price-submit': '_onSavePrice',
        },
	    init: function (parent, params) {
	        this._super.apply(this, arguments);
	        var self = this;
	        this.action_manager = parent;
	        this.params = params;
	        this.line_id = 0;
	        this.cart_lines = [];
	        this.recent_sale_order_list = [];
	        self.company_id = session.company_id;
	        this.product_id = arguments[0].product_id;
	        core.bus.on('barcode_scanned', this, function (barcode) {
	            this.scan(barcode);
	        });
	    },
	     willStart: function () {
	        var self = this;
	        var prom1 = this.check_user_rights();
	        var prom2 = this.load_companies();
	        var prom3 = this.load_currency();
	        var prom4 = this.load_all_currency();
	        return Promise.all([this._super.apply(this, arguments),prom1, prom2, prom3,prom4]).then(function(values) {
	            if(prom1 && prom2 && prom3 && prom4){
	                self.multi_company = values[1].company;
	                self.multi_currency = values[1].currency;
	                self.user_company_ids = values[2];
                    self.set_currency(values[3]);
                    self.company_currency = values[3];
                    self.currencies = values[4];
	            }
	        });
	     },

	    _compute_currency: function(e){
	    	var self = this;
	    	var currency_id = Number($(e.currentTarget).val());
	    	var order_total = self.main_order_total;
	    	var currencies = self.currencies;
	    	var invoice_date = $('#invoice_date').val();
	    	var order_untaxes = self.order_untaxes;
	    	var order_taxes = self.order_taxes;
	    	var change_currency = _.find(currencies, function(currency) { return currency.id == currency_id });
	    	self.set_currency(change_currency);
	    	if(order_total > 0 && currency_id){
	    		var params = {
            		model: 'account.move',
            		method: 'compute_currency',
            		args: [currency_id, order_untaxes,order_total, order_taxes, invoice_date],
            	}
            	rpc.query(params, {async: false})
                .then(function(result){
                	if(result.order_total){
                		var amount = result.order_total;
                		if(Number(amount)){
                    		self.set_due_amount(amount);
                    		self.set_order_total(amount)
                    		$('.due_payment_amt').text(self.format_currency(amount));
                    		$('.order_total').text(self.format_currency(amount));
                    	}
                    	_.each(self.$el.find('.paymentline'), function(element, index){
            	    		var line_element = $(element);
            	    		var elem_id = Number(line_element.attr('data-id'));
            	    		var amount = Number(line_element.find('input').val());
        	    			line_element.remove();
        	    			self.render_payment_lines();
            	    	});
                	}
                	if(result.order_taxes){
                		$('.order_taxes').text(self.format_currency(result.order_taxes));
                	}
                });
	    	}
	    },
	    slidemenubtn: function(){
	    	var self = this;
	    	$('#wrapper').removeClass('oe_hidden');
           	$('#wrapper').toggleClass("toggled");
           	$('#wrapper').find('i').toggleClass('fa fa-chevron-left fa fa-chevron-right');
           	if(!$('#wrapper').hasClass('toggled')){
           		$('#slidemenubtn').css({
           			'right':'350px',
           		});
           	}else{
           		$('#slidemenubtn').css({
           			'right':'0px',
           		});
           	}
           	var sale_orders = self.get_sale_orders();
           	$('.recent_orders_data').html('');
            var records = QWeb.render('SaleOrderLine', {
            	'sale_orders':sale_orders,
            	'widget':self,
            });
            $('.recent_orders_data').html(records);
	    },
	    load_currency: function(){
	    	var self = this;
	    	return new Promise(function (resolve, reject) {
                var params = {
                    model: 'account.move',
                    method: 'load_currency',
                    args: [self.company_id],
                }
                rpc.query(params, {async: false})
                .then(function(currency){
                    if(currency && currency[0]){

                        resolve(currency[0]);
                    }
                });
            });
	    },
	    set_currency: function(currency){
	    	var self = this;
	    	self.currency = currency;
	    	if (self.currency.rounding > 0 && self.currency.rounding < 1) {
                self.currency.decimals = Math.ceil(Math.log(1.0 / self.currency.rounding) / Math.log(10));
            } else {
                self.currency.decimals = 0;
            }
	    },
	    check_user_rights: function(){
	    	var self = this;
	    	var multi_company,multi_currency = false
	    	return new Promise(function (resolve, reject) {
                var params = {
                    model: 'account.move',
                    method: 'check_user_rights',
                    args: [session.uid],
                }
                rpc.query(params, {async: false})
                .then(function(user_rights){
                    if(user_rights){
                        if(user_rights.multi_company){
                            multi_company = true;
                        }
                        if(user_rights.multi_currency){
                            multi_currency = true;
                        }
                        if(user_rights.user){
                            self.user = user_rights.user;
                        }
                        resolve({'company':multi_company,'currency':multi_currency});
                    }
                });
            });
	    },
	    load_companies: function(){
	    	var self = this;
	    	var user_company_ids = []
	    	return new Promise(function (resolve, reject) {
                var params = {
                    model: 'res.company',
                    method: 'search_read',
                    fields: ['display_name', 'currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id' , 'country_id', 'tax_calculation_rounding_method'],
                }
                rpc.query(params, {async: false})
                .then(function(companies){
                    if(companies && companies[0]){
                        self.companies = companies;
                        self.user_company_ids = [];
                        if(self.user.company_ids.length > 0){
                            self.user.company_ids.map(function(company_id){
                                companies.map(function(company){
                                    if(company.id == company_id){
                                        user_company_ids.push(company);
                                    }
                                });
                            });
                        }
                        resolve(user_company_ids);
                    }
                });
            });
	    },
	    load_all_currency: function(){
	    	var self = this;
	    	return new Promise(function (resolve, reject) {
                var params = {
                    model: 'res.currency',
                    method: 'search_read',
                    domain: [['active','=', true]]
                }
                rpc.query(params, {async: false})
                .then(function(currencies){
                    if(currencies && currencies[0]){
                        resolve(currencies);
                    }
                });
            });
	    },
	    change_multi_company: function(e){
	    	var company_id = Number($(e.currentTarget).val());
	    	if(company_id){
	    		this.company_id = company_id;
	    	}
	    	this.set_journals();
	    },
	    set_journals: function(){
	    	var self = this;
	    	var journals = [];
	    	if(self.journals){
	    		if(self.company_id && self.journals.length > 0){
					self.journals.map(function(journal){
						if(journal.company_id[0] == self.company_id){
							journals.push(journal);
						}
					});
				}
	    	}
    		var line_html = QWeb.render('Payment-Method',{
                widget:  self,
                company_journals: journals,
            });
    		if(journals.length <=0){
    			if(self && self.state == 'paid'){
	    			var message = "Please add journals related to current company";
	    			if(self && self.notification_manager){
	    				self.do_notify('Warning: ', message , false);
	    			}
    			}
    		}
			self.$el.find('.payment-list.main-payment').html(line_html);
	    },
	    _product_delete: function(event){
	    	var self = this;
	    	var id = Number($(event.currentTarget).attr('data-id'));
	    	self.remove_cart_line_by_id(id);
	    },
	     _discount_delete: function(event){
	    	var self = this;
	    	var selected_line = this.get_selected_line();
	    	if (selected_line.discount > 0)
	    	{
	    	    selected_line.discount = 0
	    	    self.render_orderline(selected_line);
	    	}
	    	else{
                alert("No any Discount applied!");
            }
	    },
	    _sale_date_picker: function(event){
	    	$('#invoice_date').datetimepicker('show');
	    },

	    renderElement: function(){
	    	var self = this;
	    	this._super();
	    	self.load_journals();
	    	this.$el.find('.order_total').text(self.format_currency(0));
	    	var $date = this.$el.find('#invoice_date');
	    	$date.datetimepicker({
	    		format: 'MM/DD/YYYY',
	        	minDate: moment({ y: 1900 }),
	            maxDate: moment().add(200, "y"),
	            defaultDate: new Date(),
	            calendarWeeks: true,
	            icons: {
	                time: 'fa fa-clock-o',
	                date: 'fa fa-calendar',
	                next: 'fa fa-chevron-right',
	                previous: 'fa fa-chevron-left',
	                up: 'fa fa-chevron-up',
	                down: 'fa fa-chevron-down',
	                close: 'fa fa-times',
	            },
	            locale : moment.locale(),
	            allowInputToggle: true,
	        });
	    	this.$el.find(".dropdown-menu li a").click(function(){
    	        $(".btn:first-child").text($(this).text());
    	        $(".btn:first-child").val($(this).text());
    	    });
	    	this.$el.find('#customer_txt').on('keyup',function(event){
	            var query = this.value;
	            self.search_customer(query,event.which === 13);
	        });
	    	this.$el.find('.search-product input').on('keyup',function(event){
	            var query = this.value;
	            self.search_product(query,event.which === 13);
	        });
	    },
	    click_customer_txt: function(){
	    	this.search_customer();
	    },
	    search_customer: function(query, associate_result){
	    	var self = this;
	    	var $customer_txt = this.$el.find('#customer_txt');
	    	var invoice_type = this.$el.find('#invoice_type').val();
	    	var domain = [];
	    	if(query){
		    	if(invoice_type && invoice_type == 'out_invoice'){
		    		domain = [['name','ilike',query],['customer_rank','>',0]];
		    	}else if(invoice_type && invoice_type == 'in_invoice'){
		    		domain = [['name','ilike',query],['supplier_rank','>',0]];
		    	}
	    	}else{
	    		self.set_customer(null);
	    	}
    		var params = {
        		model: 'res.partner',
        		method: 'search_read',
        		domain: domain,
        		fields:['name','street','city','state_id','country_id','vat',
                        'phone','zip','mobile','email','write_date',
                        'property_account_position_id','property_product_pricelist'],
                limit:5,
        	}
        	rpc.query(params, {async: false})
            .then(function(partners){
            	var partners_list = [];
            	if(partners && partners[0]){
            		var partners = partners;
            		_.each(partners, function(partner){
            			partners_list.push({
                            'id':partner.id,
                            'value':partner.name,
                            'label':partner.name,
                    	});
                    });

            		$customer_txt.autocomplete({
                        source:partners_list,
                        select: function(event, partner){
                        	if(partner.item && partner.item.id){
                        		var partner_obj = _.find(partners, function(customer) { return customer.id == partner.item.id });
                        		if(partner_obj){
                        			self.set_customer(partner_obj);
                        		}
                        	}
                        },
                        autoFocus: true,
                        focus: function(e, ui) {
                            e.preventDefault();
                        },
                    });
            	}
            });
	    },
	    set_customer: function(customer){
	    	this.customer = customer;
	    },
	    get_customer: function(){
	    	return this.customer;
	    },
	    search_product_click: function(){
	    	this.search_product();
	    },
	    search_product: function(query, associate_result){
	    	var self = this;
	    	var $product_txt = this.$el.find('.search-product input');
	    	var domain = [];

    		var params = {
        		model: 'product.product',
        		method: 'search_read',
        		domain: domain,
        		fields:['name', 'display_name', 'list_price', 'standard_price', 'categ_id', 'taxes_id',
                        'barcode','invoice_policy'],
                limit:5,
        	}
        	rpc.query(params, {async: false})
            .then(function(products){
            	var products_list = [];
            	if(products && products[0]){
            		var products = products;
            		_.each(products, function(product){
            			products_list.push({
                            'id':product.id,
                            'value':product.display_name,
                            'label':product.display_name,
                    	});
                    });
            		$product_txt.autocomplete({
                        source:products_list,
                        select: function(event, product){
                        	if(product.item && product.item.id){
                        		var product_obj = _.find(products, function(prod) { return prod.id == product.item.id });
                        		if(product_obj){
                        		    var tax_detail = self.get_tax_amount_by_product_id(product_obj.id);
                        			var line = {
                            			'product_id': [product_obj.id, product_obj.name],
                            			'quantity':1,
                            			'display_price':product_obj.list_price,
                            			'discount': 0,
                           			    'product_tax_amount': tax_detail.total_amount || 0,
                            			'price_unit':product_obj.list_price,
                            			'price':product_obj.list_price,
                            			'invoice_policy':product_obj.invoice_policy,
                        			};

                        			self.add_orderline(line);
                        		}
                        	}
                        },
                        close: function( event, ui ) {
                        	$(event.target).val('');
                        	$(event.target).focus();
                        }
                    });
            	}
            });
	    },
	    get_tax_amount_by_product_id: function(price_unit,quantity,product_id){
	    	var self = this;
	    	var amount = 0;
	    	var company_id = self.company_id;
	    	var customer = self.get_customer();
	    	var tax_ids = [];
	    	var params = {
        		model: 'account.move',
        		method: 'get_product_tax_amount',
        		args: [price_unit,quantity,product_id, company_id, customer],
        	}
	    	rpc.query(params, {async: false})
            .then(function(taxes_details){
            	if(taxes_details && taxes_details.amount){
            		amount = taxes_details.amount;
            	}
            });
	    	var result = {
	    		total_amount:amount,
	    	}
	    	return result;
	    },
	    get_quantity: function(){
	    	return this.quantity || 1;
	    },
	    set_quantity: function(quantity){
	    	this.quantity = quantity;
	    },
	    set_order_total: function(order_total){
	    	this.order_total = order_total;
	    },
	    get_order_total: function(){
	    	return this.order_total;
	    },
	    add_orderline: function(line){
	    	var self = this;
	    	var currency = self.company_currency;
	    	var line_id = this.line_id + 1;
	    	this.line_id = line_id;
	    	line['id'] = line_id;
	    	var line_html = QWeb.render('CardLine',{
                widget:  this,
                line: line,
                image_url:this.get_product_image_url(line.product_id[0]),
            });
	    	$('.chekcout-cart-item-collection').append(line_html);
	    	this.cart_lines.push(line);
	    	self.selected_line(line_id);
	    	self.render_orderline(line);
	    	this.set_journals();
	    },
	    remove_cart_line_by_id: function(id){
	    	var self = this;
	    	_.each(this.$el.find('.cart-row-item'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.attr('data-cartline-id'));
	    		if(elem_id == id){
	    			self.set_quantity(0);
	    			line_element.remove();
	    			self.cart_lines = _.without(self.cart_lines, _.findWhere(self.cart_lines, {
	    				id: id,
	    			}));
	    		}
	    	});
	    },
	    get_product_image_url: function(product_id){
	        return window.location.origin + '/web/image?model=product.product&field=image_medium&id='+product_id;
	    },
	    _cart_line_click: function(event){
	    	var line_id = Number($(event.currentTarget).attr('data-cartline-id'));
	    	this.selected_line(line_id);
	    	if ($(event.currentTarget).hasClass("active")) {
	    		$(event.currentTarget).removeClass("active");
	        } else {
	        	$(event.currentTarget).removeClass("active");
	        	$(event.currentTarget).addClass("active");
	        }
	    },
	    selected_line: function(line_id){
	    	var self = this;
	    	$('.cart-row-item').removeClass('line_selected');
	    	$('.cart-row-item').removeClass('active');
	    	_.each(this.$el.find('.cart-row-item'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.attr('data-cartline-id'));
	    		if(elem_id == line_id){
	    			line_element.addClass('line_selected');
	    		}
	    	});
	    	self.update_summary();
	    },
	    get_selected_line: function(){
	    	var self = this;
	    	var elem_id = null;
	    	var lines = self.cart_lines;
	    	var selected_line = null;
	    	_.each(this.$el.find('.cart-row-item'), function(element, index){
	    		var line_element = $(element);
	    		if(line_element.hasClass('line_selected')){
	    			elem_id = Number(line_element.attr('data-cartline-id'));
	    		}
	    	});
	    	if(elem_id){
	    		if(lines && lines[0]){
	    			lines.map(function(line){
	    				if(line.id == elem_id){
	    					selected_line = line;
	    				}
	    			});
	    		}
	    	}
	    	if(selected_line){
	    		return selected_line;
	    	}
	    },
	    get_cart_lines: function(){
	    	return this.cart_lines || [];
	    },
        _onSaveDiscount : function(ev){
	    	var self = this;
	    	var new_data = ev.data;
	    	var val = 0 ;
	    	var selected_line = this.get_selected_line();
	    	if (new_data){
	    	    val = new_data['add_disc'];
	    	}
	    	if(selected_line){
	    	    val = new_data['add_disc'];
	    	    val = parseInt(val)
	    	    if(val<1 || val>100)
	    	    {
	    	        alert('Please Enter Valid Value!!')
	    	    }
	    	    else{
		    			selected_line.discount = val;
				        self.render_orderline(selected_line);
	    	    }

	    	}
	    	else{
                alert("Please selected line into cart!");
            }
	    },
	    _onSavePrice : function(ev){
	    	var self = this;
	    	var new_data = ev.data;
	    	var val = 0 ;
	    	var selected_line = this.get_selected_line();
	    	if (new_data){
	    	    val = new_data['add_price'];
	    	}
	    	if(selected_line){
	    	    val = new_data['add_price'];
	    	    if(val != 0){
		    			selected_line.price = val;
				        self.render_orderline(selected_line);
	    	    }
	    	    else{
                        alert("value not found!");
                    }
	    	}
	    	else{
                alert("Please selected line into cart!");
            }
	    },
        _numpad_disc_button_click:  function(){
	    	var self = this;
	    	var selected_line = this.get_selected_line();
	    	if (!selected_line)
	    	{
                alert("Please Enter Product into Cart..!!")
	    	}
	    	else{
                var discount_dialog =  new DiscountDialog (this, {
                    title: _t('Add Discount'),
                    size: 'small',
                    $content: QWeb.render('add_product_discount',{'selected_line':selected_line}),
                    buttons: [{
                        text: _t('Apply'),
                        click: function () {
                            this._onFormSubmit();
                        },
                    }],
                });
                var product_id = self.product_id;
                discount_dialog.opened().then(function () {
                    var self = this;
                    var l10n = _t.database.parameters;
                    $('#product_id').val(selected_line.product_id);
                    $('#selected_line').val(selected_line)
                });
                discount_dialog.open();
	    	}
	    },
	    _numpad_price_button_click: function(event){
	        var self = this;
	        var selected_line = this.get_selected_line();
	        if (!selected_line)
	    	{
                alert("Please Enter Product into Cart..!!")
	    	}
	    	else{
                var price_dialog =  new PriceDialog (this, {
                    title: _t('Change Price'),
                    size: 'small',
                    $content: QWeb.render('add_product_price',{'selected_line':selected_line}),
                    buttons: [{
                        text: _t('Apply'),
                        click: function () {
                            this._onFormSubmit();
                        },
                    }],
                });
                var product_id = self.product_id;
                price_dialog.opened().then(function () {
                    var self = this;
                    var l10n = _t.database.parameters;
                    $('#product_id').val(selected_line.product_id);
                    $('#selected_line').val(selected_line)
                });
                price_dialog.open();
            }
	    },
	    _qunt_minus_click: function(event){
	        var self = this;
	        var selected_line = this.get_selected_line();
	        if (selected_line.quantity > 0)
	        {
	            selected_line.quantity = selected_line.quantity - 1;
	        }
	        selected_line.quantity = selected_line.quantity;
		    self.render_orderline(selected_line);
	    },
	    _qunt_plus_click: function(event){
	        var self = this;
	        var selected_line = this.get_selected_line();
	        selected_line.quantity = selected_line.quantity + 1;
		    self.render_orderline(selected_line);
	    },
	    get_display_price: function(selected_line){
	    	var self = this;
	    	var price = (selected_line.price * selected_line.quantity * (1 - selected_line.discount/100));
	    	return price;
	    },
	    render_orderline: function(selected_line){
	    	var self = this;
	    	var price = self.get_display_price(selected_line);
	    	if(price){
	    		selected_line.display_price = price;
	    	}
	    	var tax_detail = self.get_tax_amount_by_product_id(selected_line.display_price, selected_line.quantity, selected_line.product_id[0]);
	    	if(tax_detail){
	    		selected_line.product_tax_amount = tax_detail.total_amount;
	    	}
	    	_.each($('.cart-row-item'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.attr('data-cartline-id'));
	    		var active = $('.cart-row-item.line_selected').hasClass('active');
	    		if(elem_id == selected_line.id){
	    			line_element.replaceWith(QWeb.render('CardLine',{
	                    widget:  self,
	                    line: selected_line,
	                    image_url:self.get_product_image_url(selected_line.product_id[0]),
	                }));
	    			self.selected_line(selected_line.id);
	    			_.extend(_.findWhere(self.cart_lines, { id: selected_line.id }), selected_line);
	    		}
	    		if(active){
	    			$('.cart-row-item.line_selected').addClass('active')
	    		}
	    	});
	    	self.update_summary();
	    },
	    cart_row_item_click: function(event){
	    	if ($(event.currentTarget).hasClass("active")) {
	    		$(event.currentTarget).removeClass("active");
	        } else {
	        	$(event.currentTarget).removeClass("active");
	        	$(event.currentTarget).addClass("active");
	        }
	    },
	    scan: function(code){
	    	var self = this;
	    	if (!code) {
	            return;
	        }
	    	var invoice_type = self.invoice_type;
	    	var domain = [];
    		if(invoice_type == 'in_invoice'){
    			domain = [['barcode','=',code], ['purchase_ok','=',true]];
    		}
    		if(invoice_type == 'out_invoice'){
    			domain = [['barcode','=',code], ['sale_ok','=',true]];
    		}
	    	var params = {
        		model: 'product.product',
        		method: 'search_read',
        		domain: domain,
        		fields:['name', 'display_name', 'list_price', 'standard_price', 'categ_id', 'taxes_id',
                        'barcode', 'default_code', 'to_weight', 'uom_id', 'description_sale', 'description',
                        'product_tmpl_id','tracking'],
        	}
        	rpc.query(params, {async: false})
            .then(function(product){
            	if(product && product[0]){
           		var tax_detail = self.get_tax_amount_by_product_id(product[0].id);
            		var line = {
            			'product_id': [product[0].id, product[0].name],
            			'price':product[0].list_price,
            			'quantity':1,
            			'display_price': product[0].list_price,
            			'discount': 0,
           			    'product_tax_amount': tax_detail.total_amount || 0,
            			'price_unit':product[0].list_price,
            			'invoice_policy':product[0].invoice_policy,
        			};
        			self.add_orderline(line);
            	}
            });
	    },
	    update_summary: function(){
	    	var self = this;
	    	var lines = self.cart_lines || [];
	    	var total_products = 0;
	    	var total_quantity = 0;
	    	var order_untaxes = 0;
	    	var order_total = 0;
	    	var order_taxes = 0;
	    	var product_id_list = [];
	    	lines.map(function(line){
	    		if(line.quantity > 0){
	    			total_quantity += line.quantity;
	    		}
	    		if(line.display_price > 0){
	    		    order_untaxes += (line.display_price);
	    		}
	    		if(line.display_price > 0){
	    			order_total += (line.display_price + line.product_tax_amount);
	    		}
	    		if(line.display_price > 0){
	    			order_taxes += (line.product_tax_amount);
	    		}
	    		if(($.inArray(line.product_id[0], product_id_list) == -1)){
	    			total_products += 1
	    			product_id_list.push(line.product_id[0]);
	    		}
	    	});
	    	self.set_order_total(order_total);
	    	self.main_order_total = order_total;
	    	self.order_untaxes = order_untaxes;
	    	self.order_taxes = order_taxes;
	    	self.render_payment_lines();
	    	$('.total_products').text(total_products);
	    	$('.total_quantity').text(total_quantity);
	    	$('.order_untaxes').text(self.format_currency(order_untaxes));
	    	$('.order_taxes').text(self.format_currency(order_taxes));
	    	$('.order_total').text(self.format_currency(order_total));
	    },
	    cart_content: function(e){
	    	e.stopPropagation();
	    },
	    product_qty_out: function(event){
	    	var self = this;
	    	var selected_line = this.get_selected_line();
	    	var qty = Number($(event.currentTarget).val());
	    	if(qty >= 0){
	    		self.set_quantity(qty);
				selected_line.quantity = qty;
				self.render_orderline(selected_line);
	    	}
	    },
	    product_price_out: function(event){
	    	var self = this;
	    	var selected_line = this.get_selected_line();
	    	var price = Number($(event.currentTarget).val());
	    	if(price >= 0){
				selected_line.price = price;
				self.render_orderline(selected_line);
	    	}
	    },
	    product_disc_out: function(event){
	    	var self = this;
	    	var selected_line = this.get_selected_line();
	    	var discount = Number($(event.currentTarget).val());
	    	if(discount >= 0){
				selected_line.discount = discount;
				self.render_orderline(selected_line);
	    	}
	    },
	    load_journals: function(){
	    	var self = this;
	    	var params = {
        		model: 'account.move',
        		method: 'get_invoice_journals',
        	}
        	rpc.query(params, {async: false})
            .then(function(records){
            	if(records && records[0]){
            		self.journals = records;
            		records.map(function(record){
            			var line_html = QWeb.render('Payment-Method',{
                            widget:  this,
                            journal: record,
                        });
            			self.$el.find('.payment-list.main-payment').append(line_html);
            		});
            	}
            });
	    },
	    payment_method_click: function(event){
	    	var self = this;
	    	var journals = this.journals;
	    	var lines = self.get_cart_lines();
	    	var id = Number($(event.currentTarget).attr('data-id'));
	    	if(lines && lines[0]){
	    		if(id){
		    		if(!this.payment_line_existe(id)){
		    			var journal = _.find(journals, function(jnl) { return jnl.id == id });
			    		var line_html = QWeb.render('PaymentLine',{
			                widget:  this,
			                journal:journal,
			            });
			    		$('.payment_line_area').append(line_html);
			    		this.selected_payment_line(id);
			    		self.render_payment_lines();
		    		}else{
			    		this.selected_payment_line(id);
			    	}
		    	}
		    	this.$el.find('.payment-line').show();
		    	this.$el.find('.paymentlines-empty').hide();
		    	self.set_journals();
	    	}else{
	    		var message = "<li>Please add products into cart!</li>";
	    		self.do_notify('Warning: ', '<ul>'+ message +'</ul>', false);
	    	}
	    },
	    payment_line_existe: function(id){
	    	var flag = false;
	    	_.each(this.$el.find('.paymentline'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.attr('data-id'));
	    		if(elem_id == id){
	    			flag = true;
	    		}
	    	});
	    	return flag;
	    },
	    format_currency: function(amount,precision){
	    	var self = this;
	        var currency = (self && self.currency) ? self.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
	        amount = this.format_currency_no_symbol(amount,precision);
	        if (currency.position === 'after') {
	            return amount + ' ' + (currency.symbol || '');
	        } else {
	            return (currency.symbol || '') + ' ' + amount;
	        }
	    },
	    format_currency_no_symbol: function(amount, precision) {
	    	var self = this;
	        var currency = (self && self.currency) ? self.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
	        var decimals = currency.decimals;
	        if (typeof amount === 'number') {
	            amount = round_di(amount,decimals).toFixed(decimals);
	            amount = field_utils.format.float(round_di(amount, decimals), {digits: [69, decimals]});
	        }
	        return amount;
	    },
	    create_po: function(){
	    	var self = this;
	    	var lines = self.get_cart_lines();
	    	var payment_lines = self.get_payment_line_data();
	    	var customer = self.get_customer();
	    	var sale_date = $('#invoice_date').val();
	    	var message = '';
	    	var warn = 0;
	    	if(lines.length <= 0){
	    		message += "<li>Please add products into cart!</li>";
	    		self.do_notify('Warning: ', '<ul>'+ message +'</ul>', false);
	    		return false;
	    	}
	    	if(!customer){
	    		warn = 1;
	    		message += "<li>Customer</li>";
	    	}
	    	if(!sale_date){
	    		warn = 1;
	    		message += "<li>Date</li>";
	    	}
	    	if(warn == 1){
	    		self.do_notify('The following fields are invalid: ', '<ul>'+ message +'</ul>', false);
	    	}else{
	    		if(lines && lines[0]){
	    				if(payment_lines.length <= 0){
	    					var message = "<li>Please add payment line!</li>";
	    					return self.do_warn('Warning: ', '<ul>'+ message +'</ul>', false);
	    				}else{
	    					var is_minus_amount = false;
	    					payment_lines.map(function(payment_line){
	    						if(payment_line.amount < 0){
	    							is_minus_amount = true;
	    						}
	    					});
	    					if(is_minus_amount){
	    						return self.do_notify('Warning: ', '<ul><li>The payment amount cannot be negative.</li></ul>', false);
	    					}
	    				}
	    			self.create_invoice_order();
				}else{
					alert("Please add products into cart!");
				}
	    	}
	    },
	    create_invoice_order: function(){
	    	var self = this;
	    	var lines = self.get_cart_lines();
	    	var payment_lines = self.get_payment_line_data();
	    	var customer = self.get_customer();
	    	var invoice_date = $('#invoice_date').val();
	    	var currency_id = Number($('#currency').val());
	    	var due_amount = self.get_due_amount();
	    	var company_id = self.company_id;
	    	var params = {
        		model: 'account.move',
        		method: 'create_invoice',
        		args: [lines, customer, invoice_date, payment_lines, company_id, currency_id,due_amount]
        	}
        	rpc.query(params, {async: false})
            .then(function(result){
            	if(result && result.error){
            		self.do_notify('Error', result.error, false);
            	} else if(result && result.name){
            		self.do_notify('Message', 'Invoice created successfully: '+result.name , false);
            		self.recent_sale_order_list.push(result);
            	}else if(result && !result.name && result.id){
            		self.do_notify('Message', 'Invoice created successfully!' , false);
            		self.recent_sale_order_list.push(result);
            	}
        		self.destroy_order();
        		$('.modal-backdrop').remove();
            });
	    },
	    destroy_order: function(){
	    	var self = this;
	    	var lines = self.get_cart_lines();
	    	lines.map(function(line){
	    		self.remove_cart_line_by_id(line.id);
	    	});
	    	this.cart_lines = [];
	    	this.line_id = 0;
	    	self.set_customer(null);
	    	self.renderElement();
	    },
	    recent_orders: function(event){
	    	var self = this;
	    	self.close_popover();
	    	var sale_orders = self.get_sale_orders();
			$(event.currentTarget).popover({
        		placement : 'left',
    	        html : true,
    	        title: 'Recent Invoice <a class="close_popover">X</a>',
    	        content: function () {
    	            return QWeb.render('SaleOrderLine', {
    	            	'sale_orders':sale_orders,
    	            	'widget':self,
    	            });
    	        },
        	});
			$(event.currentTarget).popover('show');
          $('.popover').delegate('a.close_popover','click', self.close_popover);
	    },
	    close_popover: function(){
        	$(".popover").popover('destroy');
        },
        get_sale_orders: function(){
        	return this.recent_sale_order_list;
        },
        td_sale_order: function(event){
        	var id = Number($(event.currentTarget).attr('data-id'));
        	if(id){
        		var url = window.location.origin + '/web#id=' + id + '&view_type=form&model=account.move';
        		window.open(url);
        	}
        },
        delete_payment_line: function(event){
        	var id = Number($(event.currentTarget).attr('data-id'));
        	if(id){
        		this.delete_payment_line_by_id(id);
        	}
        },
        selected_payment_line: function(line_id){
	    	$('.paymentline').removeClass('selected')
	    	_.each(this.$el.find('.paymentline'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.attr('data-id'));
	    		if(elem_id == line_id){
	    			line_element.addClass('selected');
	    		}
	    	});
	    	$('.paymentline.selected input').focus();
	    },
	    paymentline_click: function(event){
	    	var id = Number($(event.currentTarget).attr('data-id'));
	    	if(id){
	    		this.selected_payment_line(id);
	    	}
	    },
	    delete_payment_line_by_id: function(id){
	    	var self = this;
	    	var order_total = self.get_order_total();
	    	$('.paymentline').removeClass('selected')
	    	_.each(this.$el.find('.paymentline'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.attr('data-id'));
	    		var amount = Number(line_element.find('input').val());
	    		if(elem_id == id){
	    			line_element.remove();
	    			self.render_payment_lines();
	    		}
	    	});
	    },
	    get_payment_line_data: function(){
	    	var payment_line_data = [];
	    	_.each(this.$el.find('.paymentline'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.attr('data-id'));
	    		var amount = Number(line_element.find('input').val());
	    		var data = {
	    			'journal_id': elem_id,
	    			'amount': amount || 0,
	    		}
	    		payment_line_data.push(data);
	    	});
	    	return payment_line_data;
	    },
	    payment_input: function(){
	    	this.render_payment_lines();
	    },
	    render_payment_lines: function(){
	    	var self = this;
	    	var order_amount = self.get_order_total();
	    	var line_amount = 0;
	    	_.each(this.$el.find('.paymentline'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.attr('data-id'));
	    		var amount = Number(line_element.find('input').val());
	    		if(amount){
	    			line_amount += amount
	    		}
	    	});
	    	var due_amount = order_amount - line_amount;
	    	this.set_due_amount(Number(due_amount));
	    	$('.due_payment_amt').text(self.format_currency(self.get_due_amount()));
	    },
	    set_due_amount: function(due_amount){
	    	this.due_amount = due_amount;
	    },
	    get_due_amount: function(){
	    	return this.due_amount || 0;
	    },
	    delivery_confirm: function(){
	    	this.create_invoice_order();
	    	$('#myModal').modal('hide');
	    },
	    change_invoice_type: function(){
	    	var invoice_type = this.$el.find('#invoice_type').val();
	    	$('#customer_txt').val('');
	    	this.set_customer(null);
	    },
	    reset_order: function(){
	    	var self = this;
	    	var lines = self.get_cart_lines();
	    	lines.map(function(line){
	    		self.remove_cart_line_by_id(line.id);
	    	});
	    	this.cart_lines = [];
	    	this.line_id = 0;
	    	self.set_customer(null);
	    	self.renderElement();
	    },
	});

	ListController.include({
		renderButtons: function () {
			var self = this;
	        this._super.apply(this, arguments);
	        if(this.$buttons){
                this.$buttons.on('click', '.quick_invoice', function () {
                    self.do_action({
                        'type': 'ir.actions.client',
                        'tag': 'open_quick_invoice_view',
                    });
                });
	        }
	    }
	});

	core.action_registry.add('open_quick_invoice_view', QuickInvoiceAction);

	return {
		QuickInvoiceAction: QuickInvoiceAction,
	};
});