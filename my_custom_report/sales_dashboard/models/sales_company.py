from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesCompany(models.Model):
    _name = 'sales.company'
    _description = "Sales company"
    _rec_name = 'company_name'

    company_name = fields.Char(string="Branch")
    is_exist = fields.Char(string="Is exist")

    # fetch company data
    def company(self):
        # SQL query to fetch company data
        company_query = '''SELECT DISTINCT company, (case when company is not null 
                                then 'True' end) as is_exist from sales_summary
                                WHERE company IS NOT NULL'''
        self.env.cr.execute(company_query)
        company_list = self.env.cr.fetchall()

        # loop all companies
        for rec1 in company_list:
            # search all companies
            e_data = self.env['sales.company'].search([('company_name', '=', rec1[0])])
            # check if the company exists
            if e_data:
                e_data.write({'company_name': rec1[0],
                              'is_exist': rec1[1]})
            else:
                self.env['sales.company'].create({'id': self.id,
                                                 'company_name': rec1[0],
                                                 'is_exist': rec1[1]})

