from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesBrand(models.Model):
    _name = 'sales.brand'
    _description = "Sales brand"
    _rec_name = 'brand_name'

    brand_name = fields.Char(string="Brand Name")
    category = fields.Char(string="Category")

    # fetch sales brand data
    def brand(self):
        # SQL query to fetch sales brand data
        brand_query = '''SELECT DISTINCT brand, product_category from sales_summary WHERE brand IS NOT NULL'''
        self.env.cr.execute(brand_query)
        brand_list = self.env.cr.fetchall()

        # loop all sales brands
        for rec1 in brand_list:
            # search all brands
            b_data = self.env['sales.brand'].search([('brand_name', '=', rec1[0])])
            # check if the brand exists
            if b_data:
                b_data.write({'brand_name': rec1[0],
                              'category': rec1[1]})
            else:
                self.env['sales.brand'].create({'id': self.id,
                                                 'brand_name': rec1[0],
                                                 'category': rec1[1]})


