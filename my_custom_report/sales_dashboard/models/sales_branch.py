from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesBranch(models.Model):
    _name = 'sales.branch'
    _description = "Sales branch"
    _rec_name = 'branch_name'

    branch_id = fields.Char(string="Branch ID")
    branch_name = fields.Char(string="Branch")
    area_name = fields.Char(string="Area Code")
    company_name = fields.Char(string='Company')
    is_active_branch = fields.Boolean(string='Is Branch Active')

    # fetch sales branch data
    def branch(self):
        # db conn for live db
        conf = self.env['scm.config'].search([('active', '=', True)], limit=1)
        if conf:
            params = {'host': conf.host,
                      'port': conf.port,
                      'dbname': conf.database,
                      'user': conf.user,
                      'password': conf.password}
        db_conf = ' '.join([f"{key}={value}" for key, value in params.items()])
        dbconn = db_conf

        # SQL query to fetch sales branch data
        self.env.cr.execute('''CREATE EXTENSION IF NOT EXISTS dblink; 
                                SELECT DISTINCT c.branch, a.area_code, 
                                (CASE WHEN b.company_id = 2
                                THEN 'MUTI'
                                WHEN b.company_id = 1
                                THEN 'HSI'
								WHEN b.company_id = 3
                                THEN 'EPFC' 
                                ELSE '' END) as company_name, b.lot_stock_id, b.active
                                from sales_summary c left join dblink('%s','SELECT id, name, lot_stock_id, 
                                    company_id, active
									from stock_warehouse where company_id in (1,2,3)
									and active = true') as b(b_id int, name varchar,
										lot_stock_id varchar, company_id int, active boolean)
										on c.branch = b.name
										left join res_area_code a
								on a.branch_id = b.lot_stock_id
								where b.name is not null
								order by c.branch''' % dbconn)
        branch_list = self.env.cr.fetchall()

        # loop all sales branches
        for rec1 in branch_list:
            # search all branches
            e_data = self.env['sales.branch'].search([('branch_name', '=', rec1[0])])
            # check if the branch exists
            if e_data:
                e_data.write({'branch_name': rec1[0],
                              'area_name': rec1[1],
                              'company_name': rec1[2],
                              'branch_id': rec1[3],
                              'is_active_branch': rec1[4]})
            else:
                self.env['sales.branch'].create({'id': self.id,
                                                 'branch_name': rec1[0],
                                                 'area_name': rec1[1],
                                                 'company_name': rec1[2],
                                                 'branch_id': rec1[3],
                                                 'is_active_branch': rec1[4]})



