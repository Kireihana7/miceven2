from odoo import models, fields, api, _

class StockQuant(models.Model):
    _inherit = "stock.quant"

    currency_id_dif = fields.Many2one("res.currency", 
        string="Monto en $",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),)

    @api.depends('company_id', 'location_id', 'owner_id', 'product_id', 'quantity','value','currency_id')
    def _compute_dolar(self):
        for record in self:
            if record.value != 0:
                record[("amount_total_usd")] = record.value / record.product_id.product_tmpl_id.tax_today if record.product_id.product_tmpl_id.tax_today else record.product_id.cost_currency_id._convert(record['value'], record.currency_id_dif, record.env.company, fields.date.today())
                #record[("amount_total_usd")] = record.product_id.cost_currency_id._convert(record['value'], record.currency_id_dif, record.env.company, fields.date.today())
            else:
                record[("amount_total_usd")] = 0.0

    amount_total_usd = fields.Float(string="Referencia en Dolares",compute='_compute_dolar')




    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'amount_total_usd' not in fields:
            return super(StockQuant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(StockQuant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['amount_total_usd'] = sum(quant.amount_total_usd for quant in quants)
        return res



