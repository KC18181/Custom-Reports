from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesUsage(models.Model):
    _name = 'sales.usage'
    _description = "Sales usage"
    _rec_name = 'usage_name'

    usage_name = fields.Char(string="Usage")
    date_update = fields.Date(string="Date Updated")

    # fetch sales usage data
    def usage(self):
        # SQL query to fetch sales usage data
        usage_query = '''SELECT DISTINCT usage, CURRENT_DATE as date_update from sales_summary
                            WHERE usage IS NOT NULL'''
        self.env.cr.execute(usage_query)
        usage_list = self.env.cr.fetchall()

        # loop all usages
        for rec1 in usage_list:
            # search all usages
            g_data = self.env['sales.usage'].search([('usage_name', '=', rec1[0])])
            # check if the usage exists
            if g_data:
                g_data.write({'usage_name': rec1[0],
                              'date_update': rec1[1]})
            else:
                self.env['sales.usage'].create({'id': self.id,
                                                 'usage_name': rec1[0],
                                                 'date_update': rec1[1]})



