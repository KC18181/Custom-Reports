# -*- coding: utf-8 -*-
from odoo import models, fields, api
def default_date_format(date):
    # string formatting from 2023-07-27 to 2023 July 27
    return str(date.strftime("%Y %B %d"))


class SalesBranchWizard(models.TransientModel):
    _name = 'sales.branch.wizard'
    _description = 'Sales Branch Wizard'

    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")

    branch_filter = fields.Many2many('res.branch', string="Branch",
                                     domain=lambda self: [("id", "in", self.env.user.branch_ids.ids)])
    report_filter = fields.Selection([('sales_cash', 'Sales Cash'), ('sales_credit', 'Sales Credit'),
                                      ('sales_summary', 'Sales Summary')], string="Report Filter")

    sales_branch_ids = fields.One2many('sales.branch.list', 'sales_branch_id', string='Result')
    def get_sales_branch_excel_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/sales_dashboard/sales_branch_excel_report/%s' % (self.id),
            'target': 'new',
        }

    def sales_branch_list_view(self):
        branch_codes = self.env['res.users'].sudo().search([('id', '=', self.env.uid)]).get_codes()
        branch_codes.append('0')

        filters = ''
        if self.report_filter =='sales_cash':
            if not self.branch_filter:
                filters = "AND True"
            # if a branch was selected
            else:
                branches = ''
                for x in self.branch_filter:
                    if branches:
                        branches += ","
                    branches += f"'{x.code}'"
                branches = f"({branches})"
                filters = f'AND branch_id IN {branches}'

            cash_query = f'''SELECT cash.so_line_id,cash.salesteam,cash.date,
                                    cash.salesperson,cash.so_number,cash.customer,
                                    cash.product_category,cash.brand,cash.barcode,
                                    cash.standard_description,cash.engine_number,
                                    cash.chassis_number,cash.pricelist,cash.tags,
                                    cash.payment_term,cash.qty,cash.cost,
                                    cash.amount,cash.company,branch.name
                                    FROM sales_cash cash JOIN res_branch branch 
                                    ON cash.branch_id = branch.code  
                                    AND date(cash.date) >= '{self.date_from}' 
                                    AND date(cash.date) <= '{self.date_to}' 
                                    AND branch.code in {tuple(branch_codes)}
                                    {filters}
                                    '''
            self.env.cr.execute(cash_query)
            sales_cash_results = self.env.cr.fetchall()
            sales_cash_obj = self.env['sales.branch.list']
            sales_cash_obj.search([]).unlink()

            for sales_cash in sales_cash_results:
                quantity = sales_cash[15]
                cost = sales_cash[16]
                amount = sales_cash[17]
                print()

                if quantity is None:
                    quantity = 0
                if cost is None:
                    cost = 0.00
                if amount is None:
                    amount = 0.00

                sales_cash_obj.create({
                    'sales_branch_id': self.id,
                    'so_line_id': sales_cash[0],
                    'salesteam': sales_cash[1],
                    'date': sales_cash[2],
                    'salesperson': sales_cash[3],
                    'so_number': sales_cash[4],
                    'customer': sales_cash[5],
                    'product_category': sales_cash[6],
                    'brand': sales_cash[7],
                    'barcode': sales_cash[8],
                    'standard_description': sales_cash[9],
                    'engine_number': sales_cash[10],
                    'chassis_number': sales_cash[11],
                    'pricelist': sales_cash[12],
                    'tags': sales_cash[13],
                    'payment_term': sales_cash[14],
                    'qty': quantity,
                    'cost': cost,
                    'amount': amount,
                    'company': sales_cash[18],
                    'branch_id': sales_cash[19],

                })

        elif self.report_filter == 'sales_credit':
            if not self.branch_filter:
                filters = "AND True"
            # if a branch was selected
            else:
                branches = ''
                for x in self.branch_filter:
                    if branches:
                        branches += ","
                    branches += f"'{x.code}'"
                branches = f"({branches})"
                filters = f'AND branch_id IN {branches}'

            credit_query = f'''SELECT credit.so_line_id,
                                        credit.salesteam,
                                      credit.date,
                                      credit.salesperson,
                                      credit.so_number,
                                      credit.customer,
                                      credit.product_category,
                                      credit.brand,
                                      credit.barcode,
                                      credit.standard_description,
                                      credit.engine_number,
                                      credit.chassis_number,
                                      credit.pricelist,
                                      credit.tags,
                                      credit.payment_term,
                                      credit.qty,
                                      credit.cost,
                                      credit.amount,
                                      credit.company,
                                    branch.name
                                      FROM sales_credit credit JOIN res_branch branch
                                      ON credit.branch_id = branch.code
                                      WHERE date(credit.date) >= '{self.date_from}'
                                      AND date(credit.date) <= '{self.date_to}'
                                      AND branch.code in {tuple(branch_codes)}
                                      {filters}
                                      '''
            self.env.cr.execute(credit_query)
            sales_credit_results = self.env.cr.fetchall()
            sales_credit_obj = self.env['sales.branch.list']
            sales_credit_obj.search([]).unlink()

            for sales_credit in sales_credit_results:
                quantity = sales_credit[15]
                cost = sales_credit[16]
                amount = sales_credit[17]
                print()

                if quantity is None:
                    quantity = 0
                if cost is None:
                    cost = 0.00
                if amount is None:
                    amount = 0.00

                sales_credit_obj.create({
                    'sales_branch_id': self.id,
                    'so_line_id': sales_credit[0],
                    'salesteam': sales_credit[1],
                    'date': sales_credit[2],
                    'salesperson': sales_credit[3],
                    'so_number': sales_credit[4],
                    'customer': sales_credit[5],
                    'product_category': sales_credit[6],
                    'brand': sales_credit[7],
                    'barcode': sales_credit[8],
                    'standard_description': sales_credit[9],
                    'engine_number': sales_credit[10],
                    'chassis_number': sales_credit[11],
                    'pricelist': sales_credit[12],
                    'tags': sales_credit[13],
                    'payment_term': sales_credit[14],
                    'qty': quantity,
                    'cost': cost,
                    'amount': amount,
                    'company': sales_credit[18],
                    'branch_id': sales_credit[19],
                })


        elif self.report_filter == 'sales_summary':
            # if no branch was selected
            if not self.branch_filter:
                filters = "AND True"
            # if a branch was selected
            else:
                branches = ''
                for x in self.branch_filter:
                    if branches:
                        branches += ","
                    branches += f"'{x.code}'"
                branches = f"({branches})"
                filters = f'AND branch_id IN {branches}'

            sales_summary = f'''SELECT summary.date, summary.so_number,
                                    summary.area, summary.branch, summary.barcode,
                                    summary.brand, summary.product_category,
                                    summary.standard_description, summary.usage, summary.customer,
                                    summary.engine_number, summary.chassis_number,
                                    summary.payment_term, summary.pricelist, summary.qty,
                                    summary.cost, summary.amount, summary.company,
                                    summary.res_branch_name, branch.name,
                                    summary.sales_type, summary.invoice_date, 
                                    summary.invoice_name, summary.invoice_slip, 
                                    summary.invoice_state
                                FROM
                                    sales_summary summary
                                JOIN res_branch branch
                                  ON summary.branch_id = branch.code
                                WHERE date(summary.date) >= '{self.date_from}'
                                AND date(summary.date) <= '{self.date_to}'
                                AND branch.code in {tuple(branch_codes)}
                                {filters}
                                    '''
            self.env.cr.execute(sales_summary)
            sales_summary_results = self.env.cr.fetchall()
            sales_summary_obj = self.env['sales.branch.list']
            sales_summary_obj.search([]).unlink()

            for sales_summary in sales_summary_results:
                quantity = sales_summary[14]
                cost = sales_summary[15]
                amount = sales_summary[16]

                if quantity is None:
                    quantity = 0
                if cost is None:
                    cost = 0.00
                if amount is None:
                    amount = 0.00
                sales_summary_obj.create({
                    'sales_branch_id': self.id,
                    'date': sales_summary[0],
                    'so_number': sales_summary[1],
                    'area': sales_summary[2],
                    'branch': sales_summary[3],
                    'barcode': sales_summary[4],
                    'brand': sales_summary[5],
                    'product_category': sales_summary[6],
                    'standard_description': sales_summary[7],
                    'usage': sales_summary[8],
                    'customer': sales_summary[9],
                    'engine_number': sales_summary[10],
                    'chassis_number': sales_summary[11],
                    'payment_term': sales_summary[12],
                    'pricelist': sales_summary[13],
                    'qty': quantity,
                    'cost': cost,
                    'amount': amount,
                    'company': sales_summary[17],
                    'res_branch_name': sales_summary[18],
                    'branch_id': sales_summary[19],
                    'sales_type': sales_summary[20],
                    'invoice_date': sales_summary[21],
                    'invoice_name': sales_summary[22],
                    'invoice_slip': sales_summary[23],
                    'invoice_state': sales_summary[24],
                })

        # fetch tree and form id
        if self.report_filter == 'sales_cash' or self.report_filter == 'sales_credit':
            tree2_view_id = self.env.ref('sales_dashboard.sales_branch_tree_view').id
            form2_view_id = self.env.ref('sales_dashboard.sales_branch_form_views').id
        elif self.report_filter == 'sales_summary':
            tree2_view_id = self.env.ref('sales_dashboard.sales_summary_tree_view').id
            form2_view_id = self.env.ref('sales_dashboard.sales_summary_form_views').id

        show_summary = show_cash_credit = True
        if self.report_filter == 'sales_cash' or self.report_filter == 'sales_credit':
            show_summary = False
        elif self.report_filter == 'sales_summary':
            show_cash_credit = False


        # fetch wizard input for Excel
        for_excel = self.env.context.get('for_excel', False)
        # generate Excel file
        if for_excel:
            return

        # return date format
        date_range = "from ({dateFrom}) to ({dateTo})".format(
            dateFrom=default_date_format(self.date_from),
            dateTo=default_date_format(self.date_to), )

        return {
            'name': 'Sales Branch Report - ' + date_range,
            'res_model': 'sales.branch.list',
            'view_mode': 'tree, form',
            'view_type': 'form',
            'views': [(tree2_view_id, 'tree'), (form2_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'context': {'group_by': 'branch_id',show_cash_credit:'show_cash_credit', show_summary:'show_summary'},
            'target': 'current',
        }