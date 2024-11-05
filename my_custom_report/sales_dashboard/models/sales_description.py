from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesDescription(models.Model):
    _name = 'sales.description'
    _description = "Sales description"
    _rec_name = 'description_name'

    description_name = fields.Char(string="Standard Description")
    brand = fields.Char(string="Brand")
    product_category = fields.Char(string="Product Group")

    # fetch sales product data
    def standard_description(self):
        # SQL query to fetch sales product data
        description_query = '''WITH product_group as (SELECT DISTINCT barcode, standard_description, brand, 
                                    (CASE WHEN barcode LIKE 'TR%' THEN 'TRIMOTOR' ELSE 'MC' END) 
                                    as product_category from sales_summary)
                                    SELECT a.barcode, a.description, (CASE WHEN b.brand IS NULL THEN a.brand
									ELSE b.brand END) as brand, b.product_category 
                                    from scm_master_list_mc_data a RIGHT JOIN product_group b
                                    ON a.barcode = b.barcode
                                    WHERE a.description IS NOT NULL
                                    ORDER BY a.description'''
        self.env.cr.execute(description_query)
        description_list = self.env.cr.fetchall()

        # loop all sales products
        for rec1 in description_list:
            # search all products
            d_data = self.env['sales.description'].search([('description_name', '=', rec1[1])])
            # check if the product exists
            if d_data:
                d_data.write({'description_name': rec1[1],
                              'brand': rec1[2],
                              'product_category': rec1[3]})
            else:
                self.env['sales.description'].create({'id': self.id,
                                                 'description_name': rec1[1],
                                                 'brand': rec1[2],
                                                 'product_category': rec1[3]})

