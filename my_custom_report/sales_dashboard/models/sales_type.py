from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesType(models.Model):
    _name = 'sales.type'
    _description = "Sales type"
    _rec_name = 'type_name'

    type_name = fields.Char(string="Sales Type")
    date_update = fields.Date(string="Date Updated")

    # fetch sales type data
    def type(self):
        # SQL query to fetch sales type data
        type_query = '''SELECT DISTINCT sales_type, CURRENT_DATE as date_update from sales_summary 
                            WHERE sales_type IS NOT NULL'''
        self.env.cr.execute(type_query)
        type_list = self.env.cr.fetchall()

        # loop all sales types
        for rec1 in type_list:
            # search all sales types
            i_data = self.env['sales.type'].search([('type_name', '=', rec1[0])])
            # check if the sales type exists
            if i_data:
                i_data.write({'type_name': rec1[0],
                              'date_update': rec1[1]})
            else:
                self.env['sales.type'].create({'id': self.id,
                                                 'type_name': rec1[0],
                                                 'date_update': rec1[1]})



