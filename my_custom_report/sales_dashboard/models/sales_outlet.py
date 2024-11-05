from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesOutlet(models.Model):
    _name = 'sales.outlet'
    _description = "Sales outlet"
    _rec_name = 'outlet_name'

    outlet_name = fields.Char(string="Class Outlet")
    date_update = fields.Date(string="Date Updated")

    # fetch class outlet data
    def outlet(self):
        # SQL query to fetch class outlet data
        outlet_query = '''SELECT DISTINCT class_outlet, CURRENT_DATE as date_update from sales_summary
                                WHERE class_outlet IS NOT NULL'''
        self.env.cr.execute(outlet_query)
        outlet_list = self.env.cr.fetchall()

        # loop all class outlets
        for rec1 in outlet_list:
            # search all class outlets
            j_data = self.env['sales.outlet'].search([('outlet_name', '=', rec1[0])])
            # check if the class outlet exists
            if j_data:
                j_data.write({'outlet_name': rec1[0],
                              'date_update': rec1[1]})
            else:
                self.env['sales.outlet'].create({'id': self.id,
                                                 'outlet_name': rec1[0],
                                                 'date_update': rec1[1]})



