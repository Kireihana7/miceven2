#coding: utf-8

from odoo import _, api, fields, models

class check_company_list_sale(models.Model):
    """
    A model to avoid changing checklist in a company form (and related security troubles)
    We use it instead of res.config.settings to apply properly editable trees
    """
    _name = "check.company.list.sale"
    _description = "Check List"

    @api.depends("company_id.name")
    def _compute_name_sale(self):
        """
        Compute method for name
        """
        start_name = _("Lista de verificación por compañia")
        for checklist in self:
            checklist.name = u"{} {}".format(start_name, checklist.company_id.name)

    def _inverse_check_line_ids_sale_sale(self):
        """
        Inverse method for check_line_ids_sale
        """
        for checklist in self:
            checklist.check_line_ids_sale.write({"company_id": checklist.company_id.id})

    def _inverse_no_stages_ids_sale_sale(self):
        """
        Inverse method for no_stages_ids_sale
        """
        for checklist in self:
            checklist.no_stages_ids_sale.write({"company_no_id": checklist.company_id.id})

    name = fields.Char(
        string="Nombre",
        compute=_compute_name_sale,
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Compañía",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    check_line_ids_sale = fields.One2many(
        "sale.check.item",
        "check_company_list_sale_id",
        string="Lista de verificación",
        copy=True,
        inverse=_inverse_check_line_ids_sale_sale,
    )
    no_stages_ids_sale = fields.One2many(
        "sale.check.item",
        "check_no_company_list_id",
        string="""Determine los estatus, cuya transferencia no requiere completar las listas de verificación en la etapa actual""",
        copy=True,
        inverse=_inverse_no_stages_ids_sale_sale,
    )

    _sql_constraints = [
        (
            'company_id_uniq',
            'unique(company_id)',
            _('¡La lista de verificación debe ser única por empresa!'),
        )
    ]
