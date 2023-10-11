# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

# from attr import field
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticDistribution(models.Model):
    _inherit = 'account.analytic.distribution'

class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    agricultural_analytical_tag = fields.Boolean(string='Agricultural Analytical Tag', required=True, default=True, tracking=True)

class AccountAnalyticGroup(models.Model):
    _inherit = 'account.analytic.group'

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'
    
    agriculture_company = fields.Boolean(related='company_id.agriculture_company')
    name = fields.Char(string='Analytic Account', index=True, required=True, tracking=True)
    
    # ================= Agriculture ================= #
    agricultural_analytical_account = fields.Boolean(string='Agricultural Analytical Account', required=True, default=True, tracking=True)
    # Finca:
    finca_id = fields.Many2one('agriculture.fincas', 'Farm', index=True, tracking=True, readonly=True)
    # Actividad:
    task_id = fields.Many2one('project.task', string='Task', tracking=True, readonly=True)            
    # Actividades:
    task_ids = fields.Many2many(
        'project.task',
        'task_analytic_account_rel',
        'analytic_account_id',
        'task_id',
        string='Activities'
    )       

    # Crop Request Transaction:
    crop_request_transaction_id = fields.Many2one(
        'crop.request.transaction',
        string='Crop Request Transactions',
        tracking=True
    )     

    # Crop Request Transactions:
    crop_request_transaction_ids = fields.Many2many(
        'crop.request.transaction',
        'crop_transaction_analytic_account_rel',
        'analytic_account_id',
        'crop_request_transaction_id',
        string='Crop Request Transactions',
        tracking=True
    )           

    # Parcela:
    parcel_id = fields.Many2one('agriculture.parcelas', string='Parcel', tracking=True, readonly=True)
    # Tablón:
    tablon_id = fields.Many2one('agriculture.tablon', string='Plank', tracking=True, readonly=True)

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True, tracking=True)
    is_parent_category = fields.Boolean(string='Is it a parent category?', tracking=True)
    parent_id = fields.Many2one('account.analytic.account', 'Parent Analytic Account', index=True, ondelete='cascade', tracking=True)
    parent_path = fields.Char(index=True, tracking=True)
    child_id = fields.One2many('account.analytic.account', 'parent_id', 'Child Categories', tracking=True)
    num_parents = fields.Integer(
        'Number of Parents', compute='_compute_num_parents',
        store=True,
        tracking=True)          
    type = fields.Selection([
            ('farm', 'Farm'),
            ('activity', 'Activity'),
            ('parcel', 'Parcel'),
            ('plank', 'Plank')
        ],
        string="Type",
        required=False,
        tracking=True
    )    
     

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for analytic_account in self:
            if analytic_account.parent_id:
                analytic_account.complete_name = '%s / %s' % (analytic_account.parent_id.complete_name, analytic_account.name)
            else:
                analytic_account.complete_name = analytic_account.name
    
    @api.depends('type', 'parent_id')
    def _compute_num_parents(self):
        for rec in self:
            # rec.num_parents = rec.complete_name.count('/')
            if rec.type == 'parcel':
                rec.num_parents = 2
            elif rec.type == 'plank':
                rec.num_parents = 3
            else:                
                rec.num_parents = 0
                parents = rec.parent_id 
                while parents:
                    rec.num_parents, parents = rec.num_parents + 1, parents.parent_id 

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True    

    def name_get(self):
        
        return [
            (rec.id, rec.complete_name) for rec in self
        ]         
        
        '''
        list_name = []
        for rec in self:
            complete_name = rec.complete_name
            list_name.append((rec.id, complete_name))
        return list_name
        '''

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]                      

    '''
    @api.onchange('parent_id')
    def onchange_parent_id(self):
        complete_name = self.env['account.analytic.account'].search([('id', '=', self.parent_id.id)]).complete_name
        parent_count = complete_name.count('/')
        raise UserError(_(f'The complete name "{complete_name}" has {parent_count} parent(s)'))    
    '''

    @api.model
    def create(self, vals):
        flag = True
        error_message = '' 
        
        parent_id_value = vals.get('parent_id')
        is_parent_category = vals.get('is_parent_category')
        complete_name = self.env['account.analytic.account'].search([('id', '=', parent_id_value)]).complete_name
        if complete_name != False:
            # parent_count = complete_name.count('/')

            num_parents = 0
            parents = self.parent_id
            while parents:
                num_parents, parents = num_parents + 1, parents.parent_id 

            parent_count = num_parents
            # raise UserError(_(parent_count))   
            # if parent_count >= 3:
            if parent_count > 3:
                flag = False
                error_message = 'There must be no more than 3 parent categories.'
            else:
                # raise UserError(_(f'Dato: {parent_count}; Tipo de dato: {type(parent_count)}'))
                if parent_count == 0:
                    # UPDATE:
                    if is_parent_category == True:
                        flag = False
                        error_message = 'You cannot select a main category as a parent.'                 
                                
        if flag == False:
            raise UserError(_(error_message))
        else:
            return super(AccountAnalyticAccount, self).create(vals) 

    def write(self, vals):
        flag = True
        error_message = '' 
        
        parent_id_value = vals.get('parent_id')
        is_parent_category = vals.get('is_parent_category')
        complete_name = self.env['account.analytic.account'].search([('id', '=', parent_id_value)]).complete_name
        if complete_name != False:
            # parent_count = complete_name.count('/')
            num_parents = 0
            parents = self.parent_id
            while parents:
                num_parents, parents = num_parents + 1, parents.parent_id 

            parent_count = num_parents
            # raise UserError(_(parent_count))   
            # if parent_count >= 3:
            if parent_count > 3:
                flag = False
                error_message = 'There must be no more than 3 parent categories.'
            else:
                # raise UserError(_(f'Dato: {parent_count}; Tipo de dato: {type(parent_count)}'))
                if parent_count == 0:
                    # UPDATE:
                    if is_parent_category == True:
                        flag = False
                        error_message = 'You cannot select a main category as a parent.'                   
                                
        if flag == False:
            raise UserError(_(error_message))
        else:
            return super(AccountAnalyticAccount, self).write(vals)             

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """ Returns a list of tuples containing id, name, as internally it is called {def name_get}
            result format: {[(id, name), (id, name), ...]}
        """
        args = args or []
        connector = '|'
        domain = [connector, connector, connector, 
            ('name', operator, name), 
            ('parent_id.name', operator, name), 
            ('parent_id.parent_id.name', operator, name),
            ('parent_id.parent_id.parent_id.name', operator, name) 
        ]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    '''
    def unlink(self):
        if self.num_parents == 0:
            raise UserError(_("You cannot delete this account analytic category, it is the default generic category."))
        return super().unlink()        
    '''

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    agriculture_company = fields.Boolean(related='company_id.agriculture_company')

    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        readonly=True,
        tracking=True
    )    

    account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True, ondelete='restrict', index=True, check_company=True)
    # num_parents = fields.Integer('Number of Parents', related='account_id.num_parents')
    num_parents = fields.Integer('Number of Parents')

    '''
    finca_id = fields.Many2one(
        'agriculture.fincas',
        related='farmer_request_id.finca_id',
        string='Farm',
        tracking=True
    )     

    parcel_id = fields.Many2one(
        'agriculture.parcelas',
        related='farmer_request_id.parcel_id',
        string='Parcel',
        tracking=True
    )         

    tablon_id = fields.Many2one(
        'agriculture.tablon',
        related='farmer_request_id.tablon_id',
        string='Plank',
        tracking=True
    )       
    ''' 
    # ============================================================ #
    finca_id = fields.Many2one(
        'agriculture.fincas',
        required=False,
        string='Farm',
        tracking=True
    )     

    task_id = fields.Many2one(
        'project.task',
        required=False,
        string='Task',
        tracking=True
    )         

    parcel_id = fields.Many2one(
        'agriculture.parcelas',
        required=False,
        string='Parcel',
        tracking=True
    )         

    tablon_id = fields.Many2one(
        'agriculture.tablon',
        required=False,
        string='Plank',
        tracking=True
    )                   
    # ============================================================ #
    
    analytic_account_id_1 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 0)],
        string='Finca',
        # required=True,
        tracking=True
    )

    analytic_account_id_2 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 1)],
        string='Actividad',
        # required=True,
        tracking=True
    )        

    analytic_account_id_3 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 2)],
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_id_4 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 3)],
        string='Tablón',
        required=False,
        tracking=True
    )       

    crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=False, tracking=True)
    crop_request_transaction_line_id = fields.Integer('Transaction Line', tracking=True)       
    custom_cost_sheet_line_id = fields.Many2one(
        'agriculture.cost.sheet.lines',
        string='Job Cost Sheet Line',
        tracking=True
    )                 
    # Only for Equipments:
    vehicle_id = fields.Many2one('fleet.vehicle', related='custom_cost_sheet_line_id.vehicle_id', string='Vehicle', tracking=True, store=True)
    # Only for Labours:
    employee_id = fields.Many2one('hr.employee', related='custom_cost_sheet_line_id.employee_id', string='Employee', tracking=True, store=True)    
    # Only for Hired Services:
    partner_id = fields.Many2one('res.partner', related='custom_cost_sheet_line_id.partner_id', string='Vendor', tracking=True, store=True)  