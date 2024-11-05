from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesService(models.Model):
    _name = 'sales.service'
    _description = "Sales service"
    _rec_name = 'service_name'

    service_name = fields.Char(string="Service Type")
    date_update = fields.Date(string="Date Updated")

    # fetch service type data
    def service(self):
        # SQL query to fetch service type data
        service_query = '''SELECT DISTINCT service_type, CURRENT_DATE as date_update from sales_summary
                                WHERE service_type IS NOT NULL'''
        self.env.cr.execute(service_query)
        service_list = self.env.cr.fetchall()

        # loop all service types
        for rec1 in service_list:
            # search all service types
            l_data = self.env['sales.service'].search([('service_name', '=', rec1[0])])
            # check if the service type exists
            if l_data:
                l_data.write({'service_name': rec1[0],
                              'date_update': rec1[1]})
            else:
                self.env['sales.service'].create({'id': self.id,
                                                 'service_name': rec1[0],
                                                 'date_update': rec1[1]})



