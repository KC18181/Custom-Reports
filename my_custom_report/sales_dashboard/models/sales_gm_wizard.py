from odoo import models, fields, api


class MyWizard(models.TransientModel):
    _name = 'sales.gm.wizard'
    _description = 'Sales GM Wizard'

    end_date = fields.Date(string='End Date', required=True, default=fields.Datetime.now())

    unit_of_measure = fields.Selection([('quantity', 'Quantity'), ('value', 'Value')],
                                       string='Unit of Measure', required=True, default='value')

    def get_weekly_sales_dashboard_excel_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/sales_dashboard/get_weekly_sales_dashboard_excel_report/%s' % (self.id),
            'target': 'new',
        }
