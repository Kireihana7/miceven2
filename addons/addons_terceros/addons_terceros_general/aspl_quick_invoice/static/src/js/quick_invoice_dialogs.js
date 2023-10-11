odoo.define('aspl_quick_invoice.quick_invoice_dialogs', function (require) {
    "use strict";

    const rpc = require('web.rpc');
    const Dialog = require('web.Dialog');

    const CreateCustomer = Dialog.extend({
        events: {
            "submit": "onSubmit",
        },
        async onSubmit(e) {
            e.preventDefault();
            e.stopPropagation();

            const customer = await rpc.query({
                model: "res.partner",
                method: "create_from_quick_invoice",
                kwargs: Object.fromEntries(new FormData(e.target)),
            });
            
            if("error" in customer) return this.do_notify("Error:", customer.error, false);

            const partnerId = await rpc.query({
                model: 'res.partner',
                method: 'search_read',
                domain: [["id","=",customer.partner_id]],
                fields: [
                    'name','street','city','state_id','country_id','vat',
                    'phone','zip','mobile','email','write_date',
                    'property_account_position_id','property_product_pricelist'
                ],
                limit:1,
            });

            this.trigger_up("set-customer", partnerId[0]);
            this.do_notify("Mensaje:", partnerId[0].name + " se ha creado con éxito", false);
            this.close();
        },
    });

    const DiscountDialog = Dialog.extend({
        line: null,
        mode: "",
        events: {
            'submit form': '_onFormSubmit',
            'click .btn-primary': '_onFormSubmit',
        },
        init(_, { line, mode }) {
            this._super.apply(this, arguments);

            Object.assign(this, { line, mode });
        },
        _onFormSubmit(e) {
            if(e) e.preventDefault();

            if(!this.line) return alert(_t("Please selected line into cart!"));

            if(this.mode === "discount") {
                this.trigger_up('discount-submit', {
                    discount: $("#discount").val(),
                    line: this.line
                });
            } else {                
                this.trigger_up('price-submit', {
                    price: $("#price").val(),
                    line: this.line
                });
            }

            document.forms.namedItem("product-discount").reset();
            this.close();
        },
    });

    const PrintDialog = Dialog.extend({
        invoiceId: null,
        events: {
            "submit": "onSubmit",
        },
        init(_, { invoiceId }) {
            this._super.apply(this, arguments);
            this.invoiceId = invoiceId;
        },
        async onSubmit(e) {
            e.preventDefault();
            e.stopPropagation();

            debugger;
        },
    });

    return { CreateCustomer, DiscountDialog, PrintDialog };
});