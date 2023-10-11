odoo.define('aspl_quick_invoice.quick_invoice', function (require) {
"use strict";

    const core = require('web.core');
    const rpc = require('web.rpc');
    const session = require('web.session');
    const field_utils = require('web.field_utils');
    const AbstractAction = require('web.AbstractAction');
    const { CreateCustomer, DiscountDialog, PrintDialog } = require("aspl_quick_invoice.quick_invoice_dialogs");
    const QWeb = core.qweb;
    const _t = core._t;

    const QuickInvoiceAction = AbstractAction.extend({
        title: core._t('Invoice Order'),
        template: 'QuickInvoiceAction',
        events: {
            'click .product-delete': '_product_delete',
            'click .discount-delete': '_discount_delete',
            'click .cartline': '_cart_line_click',
            "change input[name='quantity']": "onChangeQuantity",
            'focusout input.product_qty': 'product_qty_out',
            'focusout input.product_price': 'product_price_out',
            'focusout input.product_disc': 'product_disc_out',
            'click .payment_method': 'payment_method_click',
            'click .create-order': 'create_po',
            'click .recent_orders': 'recent_orders',
            'click .td_sale_order': 'td_sale_order',
            'click .delete-payment-line': 'delete_payment_line',
            'click .paymentline': 'paymentline_click',
            'keyup .paymentline .payment-input': 'render_payment_lines',
            "input .payment-input-ref": "onInputRef",
            'click .delivery-confirm': 'delivery_confirm',
            'change #invoice_type':'change_invoice_type',
            'click .toggle-nav':'toggleNav',
            "click .reset-order": "reset_order",
            'input #product-input':'search_product',
            "input #customer_txt": "search_customer",
            "click .btn-dialog": "openDialog",
            "click .create-customer": "createCustomer",
            "change input[type='checkbox'].credit-line": "render_payment_lines",
        },
        custom_events: {
            'discount-submit': '_onSaveDiscount',
            'price-submit': '_onSavePrice',
            'set-customer': 'eventSetCustomer',
        },
        state: {
            currency: undefined,
            ref_currency: undefined,
        },
        init(parent, params) {
            this._super.apply(this, arguments);

            this.action_manager = parent;
            this.params = params;
            this.line_id = 0;
            this.cart_lines = [];
            this.credits = [];
            this.recent_sale_order_list = [];
            this.company_id = session.company_id;
            this.product_id = arguments[0].product_id;

            core.bus.on('barcode_scanned', this, this.scan);
        },
        eventSetCustomer({ data }) {
            this.set_customer(data);
            $('#customer_txt').val(data.name.toUpperCase());
        },
        async willStart() {  
            return Promise.all([
                this._super.apply(this, arguments),
                this.check_user_rights(),
                this.load_currency(),
            ]).then(([_, rights, currency]) => Object.assign(this, {
                ...rights,
                ...currency,
            }));
        },
        getSelectedCredits() {
            const selectedIds = [...document.querySelectorAll("input[type='checkbox'].credit-line")]
                .filter(($c) => $c.checked)
                .map(($c) => Number($c.dataset.lineId));

            return this.credits.filter(({ id }) => selectedIds.includes(id));
        },
        async setUserCredits() {
            this.credits = await this._rpc({
                model: "account.move",
                method: "get_payments",
                kwargs: {
                    partner_id: this.customer.id,
                }
            });

            if(!this.credits) return;

            $(".credit-lines").html(QWeb.render('CreditLines', { widget: this }));
        },
        createCustomer() {
            const NewCustomer =  new CreateCustomer(this, {
                title: "Agregar cliente",
                size: 'medium',
                $content: QWeb.render('CreateCustomer'),
                renderFooter: false,
                buttons: [],
            });

            NewCustomer.open();
        },
        onChangeQuantity(e) {
            const line = this.get_selected_line();
            const value = +(e.currentTarget.value);

            const quantity = (value <= 0) ? 1 : value;

            if((line.qty_available - quantity) < 0) {
                alert("La cantidad solicitada es menor a la disponible en el producto");
            } else {
                line.quantity = quantity;
            }

            this.render_orderline(line);
        },
        onInputRef(e) {
            const $el = e.currentTarget;

            $(`.payment-input[data-payment-name="${$el.dataset.paymentName}"]`).val($el.value / this.tasa());
            this.render_payment_lines();
        },
        tasa() {
            return +($("#tasa").val());
        },
        toggleNav() {
            $(".recent-section").toggleClass("closed open");
            $(".toggle-nav i").toggleClass("fa-chevron-left fa-chevron-right");
            $("#orders-history").remove();

            const records = QWeb.render('SaleOrderLine', {
                sale_orders: this.get_sale_orders(),
                widget: this,
                url: session.url('/web'),
            });

            $("#sidebar > section").append(records);
            $("#orders-history button").click((e) => this.onClickPrint(e.currentTarget.dataset.invoiceId));
        },
        async load_currency() {          
            return rpc.query({
                model: 'account.move',
                method: 'load_currency',
            }).then(async([currency]) => {
                const currency_ref = await rpc.query({
                    model: 'res.currency',
                    method: 'read',
                    args: [currency.parent_id[0]],
                });

                return {
                    currency: currency,
                    ref_currency: currency_ref[0],
                }
            });
        },
        get ref_currency() {
            return this.state.ref_currency;
        },
        set ref_currency(currency) {
            this.state.ref_currency = currency;
        },
        get currency() {
            return this.state.currency;
        },
        set currency(currency) {
            this.state.currency = currency;

            if (this.currency.rounding > 0 && this.currency.rounding < 1) {
                this.currency.decimals = Math.ceil(Math.log(1.0 / this.currency.rounding) / Math.log(10));
            } else {
                this.currency.decimals = 0;
            }
        },
        async check_user_rights() {
            return rpc.query({
                model: 'account.move',
                method: 'check_user_rights',
            });
        },
        set_journals() {
            let journals = this.journals.filter(({ company_id: [id] }) => id === this.company_id);

            if(!journals.length) return;

            const $PaymentMethods = QWeb.render('Payment-Method',{
                widget: this,
                journals,
            });
            
            if(!journals.length && this.state === "paid" && this.notification_manager) {
                this.do_notify('Warning: Please add journals related to current company', false);
            }

            this.$el.find('.payment-methods').html($PaymentMethods);
        },
        _product_delete(event) {
            this.remove_cart_line_by_id(+event.currentTarget.dataset.id);
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
        renderElement: function(){
            var self = this;
            this._super();
            self.load_journals();
            this.$el.find('.order_total').text(self.format_currency(0));
            this.$el.find(".dropdown-menu li a").click(function(){
                $(".btn:first-child").text($(this).text());
                $(".btn:first-child").val($(this).text());
            });

            const refCurrency = this.ref_currency;
            
            this.$el.find("#tasa").val(refCurrency.rate.toFixed(refCurrency.decimal_places));
        },
        async search_customer() {
            const $input = $('#customer_txt');
            const query = $input.val();

            if(!query) return;

            const partnerIds = await rpc.query({
                model: 'res.partner',
                method: 'search_read',
                domain: ['|',['name','ilike',query],['cedula','ilike',query]],
                fields: [
                    'name','street','city','state_id','country_id','vat',
                    'phone','zip','mobile','email','write_date',
                    'property_account_position_id','property_product_pricelist'
                ],
                limit:5,
            });
            
            if(!partnerIds || !partnerIds.length) {
                if(this.customer) this.set_customer(null);

                return;
            }

            $input.autocomplete({
                source: partnerIds.map(({ id, name }) => ({
                    id,
                    value: name,
                    label: name,
                })), 
                select: (_, partner) => {
                    this.set_customer(partnerIds.find(({ id }) => id === partner.item.id ))
                },
                autoFocus: true,
                focus(e) {
                    e.preventDefault();
                },
            });
        },
        set_customer(customer) {
            this.customer = customer;

            if(!this.customer) {
                this.credits = [];
                $(".credit-lines").html("");
            } else this.setUserCredits();
        },
        get_customer() {
            return this.customer;
        },
        async search_product() {
            const $input = $('.search-product input');
            const value = $input.val().trim();

            if(!value) return;
            
            const products = await rpc.query({
                model: 'product.product',
                method: 'search_read',
                domain: ["&", ["qty_available",">",0],"|", ["name", "ilike", value], ["default_code","ilike",value]],
                fields: [
                    'name',
                    'display_name',
                    'list_price',
                    'standard_price',
                    'categ_id',
                    'taxes_id',
                    'barcode',
                    'invoice_policy',
                    "qty_available",
                    "default_code",
                ],
                limit: 5,
            });      
            
            if(!products || !products.length) return;
            
            $input.autocomplete({
                source: products.map(({ id, display_name }) => ({
                    id,
                    value: display_name,
                    label: display_name,
                })),
                select: async (e, line) => {
                    if(!(line?.item?.id)) return;

                    const product = products.find(({ id }) => id === line.item.id);

                    if(!product) return;

                    this.add_orderline({
                        product_id: [product.id, `[${product.default_code}] ${product.name}`],
                        quantity: 1,
                        display_price: product.list_price,
                        discount: 0,
                        product_tax_amount: await this.get_tax_amount_by_product_id(product.list_price, 1, product.id),
                        price_unit: product.list_price,
                        price: product.list_price,
                        invoice_policy: product.invoice_policy,
                        qty_available: product.qty_available,
                    });

                    $input.val("");
                },
            });
        },
        async get_tax_amount_by_product_id(price_unit, quantity, product_id) {
            const amount = await rpc.query({
                model: 'account.move',
                method: 'get_product_tax_amount',
                args: [price_unit, quantity, product_id, this.company_id, this.get_customer()],
            });

            return amount || 0;
        },
        get_quantity: function(){
            return this.quantity || 1;
        },
        set_quantity(quantity) {
            this.quantity = quantity;
        },
        set_order_total: function(order_total){
            this.order_total = order_total;
        },
        get_order_total: function(){
            return this.order_total;
        },
        add_orderline(line) {
            const lineId = this.line_id + 1;
            this.line_id = line.id = lineId;

            $('.chekcout-cart-item-collection').append(QWeb.render('CardLine', { widget: this, line }));

            this.cart_lines.push(line);
            this.selected_line(lineId);
            this.render_orderline(line);
            this.set_journals();
        },
        remove_cart_line_by_id(id) {
            const $line = $(`.cartline[data-cartline-id="${id}"]`);

            this.set_quantity(0);
            $line.remove();

            this.cart_lines = this.cart_lines.filter((line) => line.id !== id);
            this.update_summary();
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
        selected_line(line_id) {
            $(".cartline").removeClass("line_selected active");
            $(`.cartline[data-cartline-id="${line_id}"]`).addClass("line_selected");
        },
        get_selected_line() {            
            const $selectedLine = document.querySelector(".cartline.line_selected");

            if(!$selectedLine) return;

            const lineId = +($selectedLine.dataset.cartlineId);

            return this.cart_lines.find((({ id }) => id === lineId));
        },
        get_cart_lines() {
            return this.cart_lines || [];
        },
        _onSaveDiscount({ data }) {
            data.line.discount = data.discount;
            this.render_orderline(data.line);
        },
        _onSavePrice({ data }) {
            data.line.price = data.price;
            this.render_orderline(data.line);
        },
        _openDialog(title, mode) {
            const line = this.get_selected_line();

            if (!line) {
                return alert("Please Enter Product into Cart..!!");
            }

            const Discount =  new DiscountDialog(this, {
                title,
                line,
                mode,
                size: 'small',
                $content: QWeb.render('add_product_discount', { mode }),
                buttons: [{
                    text: _t('Apply'),
                    click() {
                        this._onFormSubmit();
                    },
                }],
            });

            Discount.opened().then(() => $("#" + mode).val(line[mode]));
            Discount.open();
        },
        openDialog(e) {
            if(e.currentTarget.dataset.mode === "discount") {
                this._openDialog(_t('Add Discount'), "discount");
            } else {
                this._openDialog(_t('Change price'), "price");
            }
        },
        get_display_price: function(selected_line){
            var self = this;
            var price = (selected_line.price * selected_line.quantity * (1 - selected_line.discount/100));
            return price;
        },
        async render_orderline(selected_line) {
            const price = this.get_display_price(selected_line);
            
            (price) && (selected_line.display_price = price);

            const tax_detail = await this.get_tax_amount_by_product_id(
                selected_line.display_price,
                selected_line.quantity,
                selected_line.product_id[0],
            );

            (tax_detail) && (selected_line.product_tax_amount = tax_detail.total_amount);

            const $line = $(`.cartline[data-cartline-id="${selected_line.id}"]`);

            $line.replaceWith(QWeb.render('CardLine', {
                widget: this,
                line: selected_line,
            }));

            this.selected_line(selected_line.id);

            Object.assign(this.cart_lines.find(({ id }) => id === selected_line.id) || {}, selected_line);

            $('.cartline.line_selected').addClass('active');

            this.update_summary();
        },
        cart_row_item_click: function(event){
            if ($(event.currentTarget).hasClass("active")) {
                $(event.currentTarget).removeClass("active");
            } else {
                $(event.currentTarget).removeClass("active");
                $(event.currentTarget).addClass("active");
            }
        },
        async scan(code) {
            if (!code) return;

            const invoiceType = this.invoice_type;
            const domain = [['barcode','=',code]];

            if(invoiceType === 'in_invoice'){
                domain.push(['purchase_ok','=',true]);
            } else if(invoiceType == 'out_invoice') {
                domain.push(['sale_ok','=',true]);
            }

            let product = await rpc.query({
                model: 'product.product',
                method: 'search_read',
                domain,
                fields: [
                    'name',
                    'display_name',
                    'list_price',
                    'standard_price', 
                    'categ_id',
                    'taxes_id',
                    'barcode',
                    'default_code',
                    'uom_id',
                    'description_sale',
                    'description',
                    'product_tmpl_id',
                    'tracking'
                ],
                limit: 1,
            });

            if(!product) return;

            if(product instanceof Array) product = product[0];

            this.add_orderline({
                product_id: [product.id, product.name],
                price:product.list_price,
                quantity: 1,
                display_price: product.list_price,
                discount: 0,
                product_tax_amount: await this.get_tax_amount_by_product_id(product.id),
                price_unit: product.list_price,
                invoice_policy: product.invoice_policy,
            });
        },
        update_summary() {
            const lines = this.cart_lines || [];

            Object.assign(this, {
                main_order_total: lines.reduce((prev, curr) => prev + (curr.display_price + curr.product_tax_amount), 0),
                order_untaxes: lines.reduce((prev, curr) => prev + curr.display_price, 0),
                order_taxes: lines.reduce((prev, curr) => prev + curr.product_tax_amount, 0),
            });
            
            this.set_order_total(this.main_order_total);
            this.render_payment_lines();

            $('.total_products').text(new Set(lines.map(({ product_id }) => product_id[0])).size);
            $('.total_quantity').text(lines.reduce((prev, curr) => prev + curr.quantity, 0));

            const showWithRef = (amount) => [
                this.format_currency(amount), 
                this.format_currency((amount * this.tasa()), this.ref_currency)
            ].join(" / ");

            $('.order_untaxes').text(showWithRef(this.order_untaxes));
            $('.order_taxes').text(showWithRef(this.order_taxes));
            $('.order_total').text(showWithRef(this.main_order_total));
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
        load_journals() {
            rpc.query({
                model: 'account.move',
                method: 'get_invoice_journals',
            }).then((records) => {
                if(!records.length) return
                
                this.journals = records;

                const $PaymentMethods = QWeb.render('Payment-Method',{
                    widget: this,
                    journals: records,
                });

                this.$el.find('.payment-methods').html($PaymentMethods);
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
        format_currency(amount, currency) {
            currency ||= this.currency;

            amount = this.format_currency_no_symbol(amount, currency);

            const formatted = [currency.symbol || "", amount];

            if(currency.position === "after") formatted.reverse();

            return formatted.join(" ");
        },
        format_currency_no_symbol(amount, currency) {
            currency ||= this.currency;
            const decimals = currency.decimal_places;

            if (typeof amount === "number") {
                amount = field_utils.format.float(amount, {digits: [69, decimals]});
            }

            return amount;
        },
        create_po() {
            if(!confirm(_t("Esta acción no se puede deshacer"))) return;

            const lines = this.get_cart_lines();
            const payment_lines = this.get_payment_line_data();

            switch(true) {
                case !(lines?.length):
                    return this.do_notify('Warning:', "Please add products into cart", false);
                case !this.get_customer():
                    return this.do_notify('Warning:', "Debes seleccionar el cliente", false);
                case this.get_due_amount() > 0:
                    return this.do_warn('Warning:', 'Please add payment line!', false);
                case payment_lines.some(({ amount }) => amount <= 0):
                    return this.do_notify('Warning:', "The payment amount cannot be negative or zero", false);
                default:
                    return this.create_invoice_order();
            }
        },
        async create_invoice_order() {
            const lines = this.get_cart_lines();
            const payment_lines = this.get_payment_line_data();
            const customer = this.get_customer();
            const due_amount = this.get_due_amount();
            const credits = this.getSelectedCredits().map(({ id }) => id);

            const result = await rpc.query({
                model: 'account.move',
                method: 'create_invoice',
                args: [lines, customer, payment_lines, due_amount, credits]
            });

            if(result?.error){
                this.do_notify('Error', result.error, false);
            } else if(result?.name){
                this.do_notify('Message', 'Invoice created successfully: '+ result.name, false);
                this.recent_sale_order_list.push(result);
            }else if(!(result?.name) && result?.id){
                this.do_notify('Message', 'Invoice created successfully!' , false);
                this.recent_sale_order_list.push(result);
            }

            this.destroy_order();
            $('.modal-backdrop').remove();
        },
        onClickPrint(invoiceId) {
            const Print =  new PrintDialog(this, {
                size: 'medium',
                $content: QWeb.render('PrintDialog', { invoiceId }),
                renderFooter: false,
                buttons: [],
            });

            Print.open();
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
        recent_orders(event) {
            this.close_popover();
            const sale_orders = this.get_sale_orders();
            const $target = $(event.currentTarget)

            $target.popover({
                placement : 'left',
                html : true,
                title: 'Recent Invoice <a class="close_popover">X</a>',
                content: () => QWeb.render('SaleOrderLine', {
                    sale_orders: sale_orders,
                    widget: this,
                    url: session.url('/web'),
                })
            });
            $target.popover('show');
            $('.popover').delegate('a.close_popover','click', this.close_popover);
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
        selected_payment_line(line_id) {
            $('.paymentline').removeClass('selected');
            $(`.paymentline[data-id=${line_id}]`).addClass("selected");
        },
        paymentline_click(e) {
            this.selected_payment_line(+(e.currentTarget.dataset.id));
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
        render_payment_lines() {
            let lineAmount = 0;

            [...this.$el.find('.paymentline .payment-input')].forEach(($el) => {
                const VALUE = +$el.value;
                
                $(`.payment-input-ref[data-payment-name="${$el.dataset.paymentName}"]`)
                    .val(VALUE * this.tasa());
                    
                lineAmount += VALUE || 0;
            });

            if(lineAmount >= this.get_order_total() || !(this.credits?.length)) {
                $(".credit-lines").html("");
            } else {
                if(!$(".credit-lines").html()) {
                    $(".credit-lines").html(QWeb.render('CreditLines', { widget: this }));
                }

                lineAmount += this.getSelectedCredits()
                    .map(({ amount }) => Math.abs(amount))
                    .reduce((prev, curr) => prev + curr, 0);
            }

            this.set_due_amount(this.get_order_total() - lineAmount);

            const dueAmount = this.get_due_amount();
            const dueAmountText = [
                this.format_currency(dueAmount),
                this.format_currency(dueAmount * this.tasa(), this.ref_currency),
            ].join(" / ");

            $('.due_payment_amt').text(dueAmountText);

            const $return =  $(".return-amount");

            $return.text("");

            if(dueAmount < 0) $(".return-amount").text("Vuelto: " + dueAmountText);

        },
        set_due_amount: function(due_amount){
            this.due_amount = due_amount;
        },
        get_due_amount: function(){
            return this.due_amount || 0;
        },
        async delivery_confirm() {
            await this.create_invoice_order();
            $('#myModal').modal('hide');
        },
        change_invoice_type: function(){
            var invoice_type = this.$el.find('#invoice_type').val();
            $('#customer_txt').val('');
            this.set_customer(null);
        },
        reset_order() {
            this.get_cart_lines().forEach(({ id }) => this.remove_cart_line_by_id(id));
            this.cart_lines = [];
            this.line_id = 0;
            this.set_customer(null);
            this.renderElement();
        },
    });

    core.action_registry.add('open_quick_invoice_view', QuickInvoiceAction);

    return { QuickInvoiceAction };
});