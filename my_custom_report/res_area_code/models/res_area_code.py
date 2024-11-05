import psycopg2
from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook

class ResAreaCode(models.Model):
    _name = "res.area.code"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    branch_name = fields.Char(string=" Branch Name")
    branch_id = fields.Char(string="Branch ID")
    area_code = fields.Char(string="Area Code")
    active = fields.Boolean(string="Active", default=False)

    def load_area(self):
        conn = request.env['res.area.config'].scm_conn()
        cur = conn.cursor()
        cur.execute('''select f.id, g.name as branch, f.complete_name as stocklocation
                            from stock_location f, stock_warehouse g
                            where g.lot_stock_id = f.id
                            and f.company_id IN(1,2,3) 
                            group by branch,f.complete_name, f.id order by stocklocation asc''')
        db_version = cur.fetchall()
        for rec in db_version:
            s_data = self.env['res.area.code'].search([('branch_id', '=', rec[0])])
            if s_data:
                self.env['res.area.code'].write({'id': self.id,
                                                 'branch_id': rec[0],
                                                 'branch_name': rec[1]
                                                 })
            else:
                self.env['res.area.code'].create({'id': self.id,
                                                  'branch_id': rec[0],
                                                  'branch_name': rec[1]
                                                  })

        cur.close()
