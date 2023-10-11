#coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

ACESSERRORMESSAGE = _(u"""Lo sentimos, ¡pero no tiene derechos para confirmar / desaprobar  '{0}'!
Contacte a su administrador de sistemas para más información.""")


class account_check_item(models.Model):
    """
    The model to keep each item of a check list
    """
    _name = "account.check.item"
    _description = "account Order Check Item"

    @api.model
    def state_selection(self):
        """
        The method to return possible states according to a account payment
        """
        states = self.env["account.payment"]._fields["state"]._description_selection(self.env)
        return states

    @api.depends("color_sel")
    def _compute_color_account(self):
        """
        Compute method for color
        """
        for checklist in self:
            checklist.color = int(checklist.color_sel)

    name = fields.Char(
        string="¿Qué se debe hacer en esta etapa?",
        required=True,
    )
    state = fields.Selection(
        state_selection,
        string="Estatus",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Compañía",
    )
    group_ids = fields.Many2many(
        "res.groups",
        "res_groups_account_check_item_list_rel_table",
        "res_groups_id",
        "account_check_item_id",
        string="Grupo de usuario",
        help="Déjelo vacío si cualquier usuario puede confirmar este elemento de la lista de verificación"
    )
    should_be_reset = fields.Boolean(
        string="Puede ser recuperado",
        default=False,
        help="""
            Si se marca cada vez que un pedido de venta se restablece a esta etapa (por ejemplo, después de la cancelación), esta lista de verificación
             el elemento se recuperaría al estado inicial
        """,
    )
    company_no_id = fields.Many2one(
        "res.company",
        string="Compañía sin estatus",
    )
    check_company_list_account_id = fields.Many2one(
        "check.company.list.account",
        string="Lista de verificación por compañía",
    )
    check_no_company_list_id = fields.Many2one(
        "check.company.list.account",
        string="Sin etapas por compañía",
    )
    color_sel = fields.Selection(
        [
            ("1", "Rojo"),
            ("2", "Naranja"),
            ("3", "Amarillo"),
            ("4", "Azul claro"),
            ("5", "Morado oscuro"),
            ("6", "Rosa salmón"),
            ("7", "Azul medio"),
            ("8", "Azul oscuro"),
            ("9", "Fucsia"),
            ("10", "Marrón"),
            ("11", "Morado"),
        ],
        string="Color",
    )
    color = fields.Integer(
        compute=_compute_color_account,
        store=True,
        string="Color",
    )

    _order = "state, id"

    def _check_cheklist_rights(self):
        """
        The method to check rights to fill check list item
        """
        if not self.env.user.has_group("account_payment_checklist.group_account_payment_checklist_superuser"):
            for item in self:
                if item.group_ids:
                    if not (self.env.user.groups_id & item.group_ids):
                        raise AccessError(ACESSERRORMESSAGE.format(item.name))


