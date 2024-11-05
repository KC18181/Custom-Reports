from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesCategory(models.Model):
    _name = 'sales.category'
    _description = "Sales category"
    _rec_name = 'categ_name'

    categ_name = fields.Char(string="Product Group")
    date_update = fields.Date(string="Date Updated")

    # fetch product category/group data
    def category(self):
        # SQL query to product category/group data
        category_query = '''SELECT DISTINCT product_category, CURRENT_DATE as date_update from sales_summary
                                    WHERE product_category IS NOT NULL'''
        self.env.cr.execute(category_query)
        category_list = self.env.cr.fetchall()

        # loop all product categories/groups
        for rec1 in category_list:
            # search all product categories/groups
            c_data = self.env['sales.category'].search([('categ_name', '=', rec1[0])])
            # loop all product categories/groups
            if c_data:
                c_data.write({'categ_name': rec1[0],
                              'date_update': rec1[1]})
            else:
                self.env['sales.category'].create({'id': self.id,
                                                 'categ_name': rec1[0],
                                                 'date_update': rec1[1]})



