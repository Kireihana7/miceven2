# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    date_finished_aux = fields.Datetime('Forzar Fecha final')

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for production in self:
            if production.date_finished_aux:
                production.write({
                    'date_finished': self.date_finished_aux.date() if self.date_finished_aux else fields.Datetime.now()
                })
        return res


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    bom_id = fields.Many2one(
        'mrp.bom', 'Parent BoM',
        index=True, ondelete='cascade', required=True)