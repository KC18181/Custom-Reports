import psycopg2
from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesBranchList(models.TransientModel):
    _name = 'sales.branch.list'
    _description = "Sales Branch List"
    _rec_name = 'so_number'

    sales_branch_id = fields.Many2one('sales.branch.wizard', string='Sales Branch Wizard')
    so_line_id = fields.Integer(string='Sales Order Line ID')
    salesteam = fields.Char(string='Sales Team')
    date = fields.Date(string='ORDER DATE')
    salesperson = fields.Char(string='Salesperson')
    so_number = fields.Char(string='Sales Order No.')
    customer = fields.Char(string='Customer Name')
    product_category = fields.Char(string='CLASSIFICATION')
    brand = fields.Char(string='Brand')
    barcode = fields.Char(string='Barcode')
    standard_description = fields.Char(string='Description')
    usage = fields.Char(string='Usage')
    engine_number = fields.Char(string='Engine No.')
    chassis_number = fields.Char(string='Chassis Number')
    pricelist = fields.Char(string='Price List')
    tags = fields.Char(string='Tags')
    payment_term = fields.Char(string='Payment Term')
    qty = fields.Integer(string='Qty')
    cost = fields.Float(string='Cost')
    amount = fields.Float(string='Amount')
    company = fields.Char(string='Company')
    branch = fields.Char(string='Branch')
    branch_id = fields.Char(string='Branch ID')
    area = fields.Char(string='Area')
    color = fields.Char(string='Color')
    res_branch_name = fields.Char(string='Res Branch')
    sales_type = fields.Char(string='Sales Type')
    invoice_date = fields.Date(string='Invoice Date')
    invoice_name = fields.Char(string='Invoice Name')
    invoice_slip = fields.Char(string='Invoice Slip #')
    invoice_state = fields.Char(string='Invoice State')
