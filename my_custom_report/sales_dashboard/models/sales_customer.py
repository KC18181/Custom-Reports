from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesCustomer(models.Model):
    _name = 'sales.customer'
    _description = "Sales customer"
    _rec_name = 'customer_name'

    customer_name = fields.Char(string="Customer Type")
    date_update = fields.Date(string="Date Updated")

    # fetch customer type data
    def customer(self):
        # SQL query to fetch customer type data
        customer_query = '''SELECT DISTINCT customer_type, CURRENT_DATE as date_update from sales_summary
                                WHERE customer_type IS NOT NULL'''
        self.env.cr.execute(customer_query)
        customer_list = self.env.cr.fetchall()

        # loop all customer types
        for rec1 in customer_list:
            # search all customer types
            k_data = self.env['sales.customer'].search([('customer_name', '=', rec1[0])])
            # check if the customer type exists
            if k_data:
                k_data.write({'customer_name': rec1[0],
                              'date_update': rec1[1]})
            else:
                self.env['sales.customer'].create({'id': self.id,
                                                 'customer_name': rec1[0],
                                                 'date_update': rec1[1]})



