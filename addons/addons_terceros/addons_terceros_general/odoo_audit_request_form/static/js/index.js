odoo.define('odoo_audit_request_form.registrar_hallazgos', function (require) {
    "use strict";

    const ChatterTopbar = require('mail/static/src/components/chatter_topbar/chatter_topbar.js');
    const Message = require("mail/static/src/components/message/message.js");
    const { patch } = require("web.utils");

    patch(ChatterTopbar, 'odoo_audit_request_form.registrar_hallazgos', {
        hasPermission: false,
        async mounted() {
            this.hasPermission = await this.env
                .session
                .user_has_group("odoo_audit_request_form.custom_group_registrar_hallazgo")   
        
            if(!this.hasPermission) $(".registrar_hallazgo").hide();
        },
        async _onClickRegistrarHallazgo() {
            const { services, bus } = this.env;

            if(!this.hasPermission) {
                return services
                    .notification
                    .notify({
                        type: "danger",
                        message: "No tienes permisos para registrar un hallazgo",
                    });
            }

            return await bus.trigger('do-action', {
                action: {
                    name: "Registrar hallazgo",
                    type: 'ir.actions.act_window',
                    res_model: 'registrar.hallazgo',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    binding_model_id: false,
                    context: {
                        default_res_id: this.chatter.thread.id,
                        default_res_model: this.chatter.thread.model,
                    },
                },
                options: {
                    on_close: () => {
                        this.trigger('reload', { keepChanges: true });
                    }
                },
            });
        }
    });

    patch(Message, 'odoo_audit_request_form.message_style', {
        async mounted() {
            await this.env.services.rpc({
                model: 'mail.message',
                method: 'search_read',
                domain: [["id", "=", this.message.id]],
                fields: ["is_finding"],
            }, { shadow: true })
                .then((result) => {
                    if(!result.length || !result) return;

                    (result[0]?.is_finding) && (this.el.style.backgroundColor = "wheat");
                });
        }
    });

    return { Message, ChatterTopbar };
});