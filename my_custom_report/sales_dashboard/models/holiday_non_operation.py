from odoo import models, fields, api
from datetime import datetime


class HolidayNonOperation(models.Model):
    _name = 'holiday.non.operation'
    _description = 'Holiday Non Operation'

    calendar_year = fields.Char(string='Calendar Year')
    country = fields.Char(string='Country')

    holiday_lines_ids = fields.One2many('holiday.non.operation.line', 'holiday_id')


class HolidayNonOperationLine(models.Model):
    _name = 'holiday.non.operation.line'
    _description = 'Holiday Non Operation Line'

    holiday_date = fields.Date(string='Date')
    holiday_name = fields.Char(string='Name')
    holiday_type = fields.Char(string='Type')
    related_state = fields.Char(string='Related States')

    holiday_id = fields.Many2one('holiday.non.operation', string='Holiday Non Operation')


