from odoo import models, fields, api
from datetime import datetime


class MCBarcode(models.Model):
    _name = 'mc.barcode'
    _description = 'MC Barcode'

    company_id = fields.Char(string='Company')
    branch_name = fields.Char(string='Branch')
    barcode = fields.Char(string='Barcode')
    standard_des = fields.Char(string='Standard Description')
    brand = fields.Char(string='Brand')
    description = fields.Char(string='Product')
    category = fields.Char(string='Category')
    branch_id = fields.Char(string='Branch_id')
    quantity = fields.Integer(string='Quantity')
    year_date = fields.Date(string='Year')
    month_date = fields.Date(string='Target Date')
    currency_id = fields.Many2one('res.currency', string='Currency')
    subtotal = fields.Monetary(string='Total', readonly=False)
    unit_price = fields.Float(string='Unit Price', digits=(12, 2), store=True)
    amount = fields.Float(string='Amount', digits=(12, 2))
    area = fields.Char(string='Area', store=True)

    # compute unit price of the target sales
    @api.depends("amount", "quantity")
    def _compute_unit(self):
        # loop all product amounts and quantities
        for record in self:
            # if quantity is at 0, the unit price is 0
            if record.quantity > 0:
                record.unit_price = record.amount / record.quantity

