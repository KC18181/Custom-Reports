from odoo import models, fields, api
from datetime import datetime


class TargetCPMRPConfig(models.Model):
    _name = 'target.cpmrp.config'
    _description = 'Target Config'

    target_date = fields.Date(string='Target Date')
    target_quantity = fields.Char(string='Quantity')
    target_value = fields.Char(string='Amount')
    target_company = fields.Char(string='Company')
    target_branch = fields.Char(string='Branch')
    target_area = fields.Char(string='Area')
    target_category = fields.Char(string='Classification')