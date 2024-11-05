from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesArea(models.Model):
    _name = 'sales.area'
    _description = "Sales area"
    _rec_name = 'area_name'

    area_name = fields.Char(string="Area")
    branch_codes = fields.Char(string="Date Updated")

    # restrict areas shown in filter based on user's allowed branches
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # set context to True or False
        context = self._context or {}
        # if filter_area is False
        if self.env.context.get('filter_area', False):
            areas = []
            # loop all user's allowed branches
            for br in self.env.user.branch_ids:
                # SQL query to check areas using user's allowed branch codes
                self._cr.execute(f"""
                    select id from sales_area where branch_codes like '%{br.code}%'
                    limit 1
                """)
                area = self._cr.fetchall()
                # if area from query doesn't exist
                if area not in areas:
                    areas += area
            # if area from query does exist
            if areas:
                args += [('id', 'in', tuple(areas))]
        # return areas
        return super(SalesArea, self)._search(args, offset, limit, order, count=count,
                                              access_rights_uid=access_rights_uid)

    # fetch sales area data
    def area(self):
        # SQL query to fetch area data
        area_query = '''SELECT (CASE WHEN area_code IS NULL THEN '' ELSE area_code END) as area_code, 
                        string_agg(branch_id, ', ' ORDER BY branch_id) AS codes
                        FROM scm_area_code
                        GROUP BY 1'''
        self.env.cr.execute(area_query)
        area_list = self.env.cr.fetchall()
        # loop all sales areas
        for rec1 in area_list:
            # search all areas
            f_data = self.env['sales.area'].search([('area_name', '=', rec1[0])])
            # check if the area exists
            if f_data:
                f_data.write({'area_name': rec1[0],
                              'branch_codes': rec1[1]})
            else:
                self.env['sales.area'].create({'id': self.id,
                                                 'area_name': rec1[0],
                                                 'branch_codes': rec1[1]})



