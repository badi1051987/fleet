# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning


class FleetTrans(models.TransientModel):
    _name = 'fleet.trans'
    _description = 'Fleet Transient Model'
    
    date_from = fields.Date('من تاريخ')
    date_to = fields.Date('الى تاريخ')
    partner_id = fields.Many2one('res.partner')
    costing_type = fields.Selection(
        selection=[
            ('load', 'وزن التحميل'),
            ('drop', 'وزن التنزيل'),
            ('max', 'اقل وزن'),
            ('min', 'اعلى وزن'),
        ],
        string='طبيعة الفونره',
        default='load'
    )
    def action_create_invoice(self):
        line = self.env['account.move.line']
        product=self.env['product.product'].search([('default_code','=','cost_product')], limit=1)
        if not product:
            product = self.env['product.product'].create({'name':'تكلفة نقل',
                                                'default_code':'cost_product',
                                                'detailed_type':'service',
                                                'list_price':1})
        product_deduct=self.env['product.product'].search([('default_code','=','cost_product_deduct')], limit=1)
        if not product:
            product_deduct = self.env['product.product'].create({'name':'خصمومات النقل',
                                                'default_code':'cost_product_deduct',
                                                'detailed_type':'service',
                                                'list_price':1})
        for rec in self:
            vals=self.env['fleet.vehicle.log.services']._read_group(
                                            domain=[('customer_id','=',rec.partner_id.id),
                                                    ('date','>=',rec.date_from),
                                                    ('date','<=',rec.date_to)],
                                            fields=['drop_weight','amount','load_weight','deduction_amnt','leak_amnt'],  
                                            groupby=['vehicle_id']
                                            )
            if len(vals)>0:
                invoice = self.env['account.move'].create({'partner_id':rec.partner_id.id,
                                                        'move_type':'out_invoice'})
                for val in vals:
                    vehicle = self.env['fleet.vehicle'].search([('id','=',val['vehicle_id'][0])]).license_plate
                    if rec.costing_type=='load':
                        line.create({'product_id':product.id,
                                     'name':vehicle,
                                     'move_id':invoice.id,
                                     'quantity':val['load_weight'],
                                     'price_unit':val['amount']})
                    elif rec.costing_type=='drop':
                        line.create({'product_id':product.id,
                                     'name':vehicle,
                                     'move_id':invoice.id,
                                     'quantity':val['drop_weight'],
                                     'price_unit':val['amount']})
                    elif rec.costing_type=='max':
                        qty = val['drop_weight'] if val['drop_weight'] < val['load_weight'] else val['load_weight']
                        line.create({'product_id':product.id,
                                     'name':vehicle,
                                     'move_id':invoice.id,
                                     'quantity':qty,
                                     'price_unit':val['amount']})
                    else:
                        qty = val['drop_weight'] if val['drop_weight'] > val['load_weight'] else val['load_weight']
                        line.create({'product_id':product.id,
                                     'name':vehicle,
                                     'move_id':invoice.id,
                                     'quantity':qty,
                                     'price_unit':val['amount']})
                    line.create({'product_id':product_deduct.id,
                                 'name':vehicle,
                                 'move_id':invoice.id,
                                 'quantity':1,
                                 'price_unit':(val['deduction_amnt']+val['leak_amnt'])})
            else:
                raise ValidationError(_('لا يوجد شحنات من هذه الشركه'))
    
    def action_create_vendor_bill(self):
        line = self.env['account.move.line']
        product=self.env['product.product'].search([('default_code','=','cost_product')], limit=1)
        if not product:
            product = self.env['product.product'].create({'name':'تكلفة نقل',
                                                'default_code':'cost_product',
                                                'detailed_type':'service',
                                                'list_price':1})
        product_deduct=self.env['product.product'].search([('default_code','=','cost_product_deduct')], limit=1)
        if not product:
            product_deduct = self.env['product.product'].create({'name':'خصمومات النقل',
                                                'default_code':'cost_product_deduct',
                                                'detailed_type':'service',
                                                'list_price':1})
        for rec in self:
            services = self.env['fleet.vehicle.log.services'].search([('vendor_id','=',rec.partner_id.id),
                                                                          ('date','>=',rec.date_from),
                                                                          ('date','<=',rec.date_to)])
            if len(services)>0:
                bill = self.env['account.move'].create({'partner_id':rec.partner_id.id,
                                                        'move_type':'in_invoice'})
            else:
                raise ValidationError(_('لا يوجد شحنات لهذه الشركه')) 
            qty=0
            cost=0
            deduct=0
            leak=0
            for service in services:
                if service.costing_type=='load':
                    qty+=service.load_weight
                    cost+=service.amount
                    deduct+=service.deduction_amnt
                    leak+=service.leak_amnt
                elif service.costing_type=='drop':
                    qty+=service.drop_weight
                    cost+=service.amount
                    deduct+=service.deduction_amnt
                    leak+=service.leak_amnt
                elif service.costing_type=='max':
                    qty+=service.drop_weight if service.drop_weight > service.load_weight else service.load_weight
                    cost+=service.amount
                    deduct+=service.deduction_amnt
                    leak+=service.leak_amnt
                else:
                    qty+=service.drop_weight if service.drop_weight < service.load_weight else service.load_weight
                    cost+=service.amount
                    deduct+=service.deduction_amnt
                    leak+=service.leak_amnt
                    
            line.create({'product_id':product.id,
                         'move_id':bill.id,
                         'quantity':qty,
                         'price_unit':cost})
            line.create({'product_id':product_deduct.id,
                         'move_id':bill.id,
                         'quantity':1,
                         'price_unit':-(deduct+leak)})
            
            
            
            
            