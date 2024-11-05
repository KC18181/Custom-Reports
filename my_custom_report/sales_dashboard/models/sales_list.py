# -*- coding: utf-8 -*-
import psycopg2
from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesList(models.TransientModel):
    _name = 'sales.list'
    _description = "Sales List"
    _rec_name = 'grp'

    wizard1_id = fields.Many2one('sales.wizard', string='Wizard ID')
    grouping = fields.Char(string='Grouping')
    grp = fields.Char(string='Group')

    wizard2_id = fields.Many2one('sales.wizard', string='Wizard ID', )
    actual_last_month_qty = fields.Integer(string='Actual Last Month (Qty)')
    actual_last_week_qty = fields.Integer(string='Actual Last Week (Qty)')
    actual_this_month_qty = fields.Integer(string='Actual This Month (Qty)')
    actual_this_week_qty = fields.Integer(string='Actual This Week (Qty)')
    target_this_month_qty = fields.Integer(string='Target This Month (Qty)')
    target_this_week_qty = fields.Integer(string='Target This Week (Qty)')
    variance_vs_last_month_qty = fields.Integer(string='Variance versus Last Week (Qty)')
    variance_vs_target_qty_month = fields.Integer(string='Variance versus Target (Qty)')
    percentage_actual_vs_target_qty_month = fields.Float(string='% Actual versus Target', digits=(12, 2))
    variance_vs_last_week_qty = fields.Integer(string='Variance versus Last Month (Qty)')
    variance_vs_target_qty_week = fields.Integer(string='Variance versus Target (Qty)')
    percentage_actual_vs_target_qty_week = fields.Float(string='% Actual versus Target', digits=(12, 2))
    actual_ytd_qty = fields.Integer(string='Actual YTD (Qty)')
    target_ytd_qty = fields.Integer(string='Target YTD (Qty)')
    variance_vs_target_ytd_qty = fields.Integer(string='Variance versus Target YTD (Qty)')
    percentage_ytd_actual_vs_target_qty = fields.Float(string='% YTD Actual versus Target', digits=(12, 2))
    actual_ytd_last_year_qty = fields.Integer(string='Actual YTD Last Year (Qty)')
    actual_last_month_value = fields.Float(string='Actual Last Month (PHP)', digits=(12, 2))
    actual_last_week_value = fields.Float(string='Actual Last Week (PHP)', digits=(12, 2))
    actual_this_month_value = fields.Float(string='Actual This Month (PHP)', digits=(12, 2))
    actual_this_week_value = fields.Float(string='Actual This Week (PHP)', digits=(12, 2))
    target_this_month_value = fields.Float(string='Target This Month (PHP)', digits=(12, 2))
    target_this_week_value = fields.Float(string='Target This Week (PHP)', digits=(12, 2))
    variance_vs_last_month_value = fields.Float(string='Variance versus Last Month (PHP)', digits=(12, 2))
    variance_vs_target_value_month = fields.Float(string='Variance versus Target (PHP)', digits=(12, 2))
    percentage_actual_vs_target_value_month = fields.Float(string='% Actual versus Target', digits=(12, 2))
    variance_vs_last_week_value = fields.Float(string='Variance versus Last Week (PHP)', digits=(12, 2))
    variance_vs_target_value_week = fields.Float(string='Variance versus Target (PHP)', digits=(12, 2))
    percentage_actual_vs_target_value_week = fields.Float(string='% Actual versus Target', digits=(12, 2))
    actual_ytd_value = fields.Float(string='Actual YTD (PHP)', digits=(12, 2))
    target_ytd_value = fields.Float(string='Target YTD (PHP)', digits=(12, 2))
    variance_vs_target_ytd_value = fields.Float(string='Variance versus Target YTD (PHP)', digits=(12, 2))
    percentage_ytd_actual_vs_target_value = fields.Float(string='% YTD Actual versus Target', digits=(12, 2))
    actual_ytd_last_year_value = fields.Float(string='Actual YTD Last Year (PHP)', digits=(12, 2))


