from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _description='Fleet Vehicle enhancment'
    
    vendor_id = fields.Many2one('res.partner', 'Vehicle Vendor', related='driver_id.parent_id')
    customer_id = fields.Many2one('res.partner', 'Customer')
    ivoice_count = fields.Integer(compute='compute_invoice_count')

    def create_invoice(self):
        account_obj= self.env['account.move']
        product=self.env['product.product'].search([('default_code','=','cost_product')], limit=1)
        line = self.env['account.move.line']
        for rec in self:
            trips=self.env['fleet.vehicle.log.services'].search([('active','=',True),
                                                             ('state','=','done'),
                                                             ('vehicle_id','=',rec.id)])
            if len(trips)>0:
                if rec.customer_id:
                    l=account_obj.create({'partner_id':rec.customer_id.id,
                                                 'move_type': 'out_invoice'})
                    line.create({'product_id':product.id,
                                 'move_id':l.id,
                                 'quantity':len(trips),
                                 'price_unit':sum(trips.mapped('amount'))})
                else:
                    raise ValidationError(_('Please insert the client at Vehicle form.'))
            else:
                raise ValidationError(_('There is no done trips.'))
                
    #     """count related visits"""
    def compute_invoice_count(self):
        for record in self:
            record.ivoice_count = self.env['account.move'].search_count(
                [('partner_id', '=', record.customer_id.id)])
    
    #     action get related visits 
    def get_invoice(self):
        self.ensure_one()
        ctx = self._context.copy()
        return {
            'type': 'ir.actions.act_window',
            'name': 'AccountMove',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('partner_id', '=', self.customer_id.id)],
            'context': "{'create':False}"
        }
            
class FleetVehicleServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _description='fleet.vehicle.log.services.inherit'
    
    vendor_id = fields.Many2one('res.partner', 'شركة النقل', related='purchaser_id.parent_id', store=True)
    customer_id = fields.Many2one('res.partner', 'الزبون')
    load_weight = fields.Float('وزن التحميل')
    drop_weight = fields.Float('وزن التنزيل')
    axial_weight = fields.Float('الوزن المحوري')
    car_weight = fields.Float('وزن السياره')
    total_weight = fields.Float('الوزن الاجمالي', compute='compute_total_weight', store=True)
    deduction_amnt= fields.Float('مبلغ الخصم')
    leak_amnt= fields.Float('مبلغ خصم التسريب')
    costing_type = fields.Selection(
        string='ألية الفوتره',
        related='customer_id.costing_type'
    )  
    
    @api.depends('load_weight','car_weight')
    def compute_total_weight(self):
        for rec in self:
            rec.total_weight=rec.load_weight+rec.car_weight
    

class ResPartner(models.Model):
    _inherit='res.partner'
    _description='fleet partner inherit'
    
    
    costing_type = fields.Selection(
        selection=[
            ('load', 'loading Weight'),
            ('drop', 'Dropping Weight'),
            ('max', 'Max Weight'),
            ('min', 'Min Weight'),
        ],
        string='Costing Type',
        default='load'
    )  
    services_count = fields.Integer(compute='compute_services_count')
    #     """count related services"""
    def compute_services_count(self):
        for record in self:
            record.services_count = self.env['fleet.vehicle.log.services'].search_count(
                ['|',('vendor_id', '=', record.id),('customer_id', '=', record.id)])
    
    #     action get related services 
    def get_services(self):
        self.ensure_one()
        ctx = self._context.copy()
        return {
            'type': 'ir.actions.act_window',
            'name': 'FleetVehicleServices',
            'view_mode': 'list,form',
            'res_model': 'fleet.vehicle.log.services',
            'domain': ['|',('vendor_id', '=', self.id),('customer_id', '=', self.id)],
            'context': "{'create':False}"
        }
        
     

     
     
     
     