from odoo import fields, models, _, api
from odoo.exceptions import  UserError

class AccountAsset(models.Model):
    _inherit = "account.asset"

    original_stock_move_ids = fields.Many2many('stock.move', 'asset_stock_move_rel', 'asset_id', 'line_id', string='Inventario', domain="[('state', '=', 'done')]", readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    # asset_id = fields.Many2one('account.asset', string='Asset', index=True, ondelete='cascade', copy=False, domain="[('company_id', '=', company_id)]")
    
    @api.depends('original_move_line_ids','original_stock_move_ids')
    def _compute_name(self):
        res = super(AccountAsset,self)._compute_name()
        for record in self:
            record.name = ''
            if len(record.original_move_line_ids)>0:
                record.name = record.name or (record.original_move_line_ids and record.original_move_line_ids[0].name or '')
            if len(record.original_stock_move_ids)>0  :
                record.name = record.name or (record.original_stock_move_ids and record.original_stock_move_ids[0].product_id.name or '')
                # raise UserError(('Precio: %s, cantidad %s')%(record.original_stock_move_ids[0].price_unit,record.original_stock_move_ids[0].quantity_done))
                record.original_value = record.original_stock_move_ids[0].price_unit #* record.original_stock_move_ids[0].quantity_done
                record.acquisition_date = record.original_stock_move_ids[0].date
                record.company_id = record.original_stock_move_ids[0].company_id
                record.analytic_tag_ids = record.original_stock_move_ids[0].analytic_tag_ids
                record.account_depreciation_id = record.original_stock_move_ids[0].product_id.categ_id.property_account_income_categ_id.id 
                record.account_depreciation_expense_id = record.original_stock_move_ids[0].product_id.categ_id.property_account_expense_categ_id.id
            