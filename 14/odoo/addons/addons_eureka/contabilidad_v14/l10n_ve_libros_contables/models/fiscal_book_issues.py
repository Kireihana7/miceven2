import time
from odoo import fields, models, api, _

class FiscalBookIssues(models.Model):
    _description = "Venta y compra de líneas de libros fiscales en Venezuela Issues"
    _name = 'fiscal.book.issues'

    name = fields.Char("Líneas de libros fiscales")
    fiscal_id = fields.Many2one('fiscal.book', 'Fiscal Book',
    help='Libro fiscal que posee esta línea de libro', ondelete='cascade', index=True)
    invoice_id = fields.Many2one('account.move', 'Factura',
    help="Factura relacionada con esta línea de libro")
    partner_name = fields.Char(size=128, string='Nombre de la Empresa', help='')