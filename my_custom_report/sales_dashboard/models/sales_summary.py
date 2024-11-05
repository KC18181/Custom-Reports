# -*- coding: utf-8 -*-
import psycopg2
from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesSummary(models.Model):
    _name = 'sales.summary'
    _description = "Sales Summary"
    _rec_name = 'so_number'

    so_line_id = fields.Integer(string='Sale Order Line ID')
    date = fields.Date(string='ORDER DATE')
    so_number = fields.Char(string='Sales Order No.')
    area = fields.Char(string='Area')
    branch = fields.Char(string='Branch')
    barcode = fields.Char(string='Barcode')
    brand = fields.Char(string='Brand')
    product_category = fields.Char(string='CLASSIFICATION')
    standard_description = fields.Char(string='Description')
    usage = fields.Char(string='Usage')
    customer = fields.Char(string='Customer Name')
    engine_number = fields.Char(string='Engine No.')
    chassis_number = fields.Char(string='Chassis Number')
    payment_term = fields.Char(string='Payment Term')
    pricelist = fields.Char(string='Pricelist')
    qty = fields.Integer(string='Qty')
    cost = fields.Float(string='Cost')
    amount = fields.Float(string='Amount')
    company = fields.Char(string='Company')
    branch_id = fields.Char(string='Branch ID')
    res_branch_name = fields.Char(string='ResBranch Name')
    sales_type = fields.Char(string='Sales Type')
    invoice_date = fields.Date(string='Invoice Date')
    invoice_name = fields.Char(string='Invoice Name')
    invoice_slip = fields.Char(string='Invoice Slip #')
    invoice_state = fields.Char(string='Invoice State')
    company_id = fields.Char(string='Company ID')
    vendor_id = fields.Char(string='Vendor_ID')
    vendor_name = fields.Char(string='Vendor Name')

    def load_summary(self):
        # SQL query to fetch area data
        summary_query = f'''WITH cash_data AS (
    SELECT
        cash.so_line_id::integer,
        cash.date::date, 
        cash.so_number::varchar,
        area.area_code::varchar, 
        area.branch_name::varchar, 
        cash.barcode::varchar,
        cash.brand::varchar, 
        cash.product_category::varchar,
        cash.standard_description::varchar, 
        cash.usage::varchar, 
        cash.customer::varchar,
        cash.engine_number::varchar, 
        cash.chassis_number::varchar,
        cash.payment_term::varchar, 
        cash.pricelist::varchar, 
        cash.qty::numeric,
        cash.cost::numeric, 
        cash.amount::numeric, 
        cash.company::varchar,
        cash.company_id::integer,
        branch.name::varchar AS branch_name, 
        area.branch_id::integer, 
        'Cash'::varchar AS sales_type,
        cash.invoice_date::date AS invoice_date,
        cash.invoice_name::varchar,
        cash.invoice_slip::varchar, 
        cash.invoice_state::varchar,
        cash.vendor_id::integer,
        cash.vendor_name::varchar
    FROM
        sales_cash cash
    JOIN
        res_branch branch ON cash.branch_id = branch.code
    JOIN
        res_area_code area ON branch.code = area.branch_id
),
credit_data AS (
    SELECT
        credit.so_line_id::integer,
        credit.date::date, 
        credit.so_number::varchar,
        area.area_code::varchar, 
        area.branch_name::varchar, 
        credit.barcode::varchar,
        credit.brand::varchar, 
        credit.product_category::varchar,
        credit.standard_description::varchar, 
        credit.usage::varchar, 
        credit.customer::varchar,
        credit.engine_number::varchar, 
        credit.chassis_number::varchar,
        credit.payment_term::varchar, 
        credit.pricelist::varchar, 
        credit.qty::numeric,
        credit.cost::numeric, 
        credit.amount::numeric, 
        credit.company::varchar,
        credit.company_id::integer,
        branch.name::varchar AS branch_name, 
        area.branch_id::integer, 
       'Installment'::varchar AS sales_type,
        credit.invoice_date::date AS invoice_date,
        credit.invoice_name::varchar,
        credit.invoice_slip::varchar, 
        credit.invoice_state::varchar,
        credit.vendor_id::integer,
        credit.vendor_name::varchar
    FROM
        sales_credit credit
    JOIN
        res_branch branch ON credit.branch_id = branch.code
    JOIN
        res_area_code area ON branch.code = area.branch_id
)

SELECT * FROM cash_data 
UNION DISTINCT
SELECT * FROM credit_data;

                        '''

        self.env.cr.execute(summary_query)
        summary_list = self.env.cr.fetchall()

        SalesSummary = self.env['sales.summary']
        ids = [id[0] for id in summary_list]
        SalesSummary.search([('so_line_id', 'not in', ids)]).unlink()

        # loop all sales areas
        for rec1 in summary_list:
            # search all areas
            s_data = self.env['sales.summary'].search([('so_line_id', '=', rec1[0])])
            # check if the area exists
            if s_data:
                s_data.write({'so_line_id': rec1[0],
                              'date': rec1[1],
                              'so_number': rec1[2],
                              'area': rec1[3],
                              'branch': rec1[4],
                              'barcode': rec1[5],
                              'brand': rec1[6],
                              'product_category': rec1[7],
                              'standard_description': rec1[8],
                              'usage': rec1[9],
                              'customer': rec1[10],
                              'engine_number': rec1[11],
                              'chassis_number': rec1[12],
                              'payment_term': rec1[13],
                              'pricelist': rec1[14],
                              'qty': rec1[15],
                              'cost': rec1[16],
                              'amount': rec1[17],
                              'company': rec1[18],
                              'company_id': rec1[19],
                              'res_branch_name':rec1[20],
                              'branch_id': rec1[21],
                              'sales_type': rec1[22],
                              'invoice_date': rec1[23],
                              'invoice_name': rec1[24],
                              'invoice_slip': rec1[25],
                              'invoice_state': rec1[26],
                              'vendor_id': rec1[27],
                              'vendor_name': rec1[28]
                            })
            else:
                self.env['sales.summary'].create({'id': self.id,
                                                'so_line_id': rec1[0],
                                                'date': rec1[1],
                                                'so_number': rec1[2],
                                                'area': rec1[3],
                                                'branch': rec1[4],
                                                'barcode': rec1[5],
                                                'brand': rec1[6],
                                                'product_category': rec1[7],
                                                'standard_description': rec1[8],
                                                'usage': rec1[9],
                                                'customer': rec1[10],
                                                'engine_number': rec1[11],
                                                'chassis_number': rec1[12],
                                                'payment_term': rec1[13],
                                                'pricelist': rec1[14],
                                                'qty': rec1[15],
                                                'cost': rec1[16],
                                                'amount': rec1[17],
                                                'company': rec1[18],
                                                'company_id': rec1[19],
                                                'res_branch_name': rec1[20],
                                                'branch_id': rec1[21],
                                                'sales_type': rec1[22],
                                                'invoice_date': rec1[23],
                                                'invoice_name': rec1[24],
                                                'invoice_slip': rec1[25],
                                                'invoice_state': rec1[26],
                                                 'vendor_id': rec1[27],
                                                  'vendor_name': rec1[28]
                                                })

        self.env['sales.summary'].search([('so_line_id', '=', rec1[0])]).unlink()       
