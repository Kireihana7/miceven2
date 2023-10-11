import time
from odoo import fields, models, api, _

class FiscalBookRetention(models.Model):
    _description = "Retentions de líneas de libros fiscales en Venezuela Issues"
    _name = 'fiscal.book.retention'

    name = fields.Char("Líneas de libros fiscales")
    fiscal_id = fields.Many2one('fiscal.book', 'Fiscal Book',
    help='Libro fiscal que posee esta línea de libro', ondelete='cascade', index=True)
    invoice_id = fields.Many2one('account.move', 'Facturas')
    retention_id = fields.Many2one('account.wh.iva', 'Retención')
    retention_line_id = fields.Many2one('account.wh.iva.line', 'Línea de Retención')
    ret_amount = fields.Float(string="Monto de Retención")
    rate_amount = fields.Float(string="Porcentaje de Retención")
    date = fields.Date(string='Fecha de la retención')