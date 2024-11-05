# -*- coding: utf-8 -*-
import psycopg2
from odoo import http
from odoo.http import content_disposition, request
import io
import xlsxwriter
import calendar
from datetime import datetime, timedelta, date


def default_date_format(date):
    # string formatting from 2023-07-27 to 2023 July 27
    return str(date.strftime("%Y %B %d"))


class STSExcelReportController(http.Controller):
    @http.route([
        '/sales_dashboard/sales_branch_excel_report/<model("sales.branch.wizard"):wizard>',
    ], type='http', auth="user", csrf=False)
    # create Excel file of ABC report containing sales data based on date
    def get_sales_branch_excel_report(self, wizard=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Sales Branch Report' + '.xlsx'))
            ]
        )

        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 14, 'bold': True, 'align': 'center', 'num_format': 'd mmm yyyy'})
        branch_title_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 14, 'bold': True, 'align': 'center',
             'bg_color': '#faeaac', 'font_color': '#000000'})
        company_title_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 14, 'bold': True, 'align': 'center', 'bg_color': '#95bff5',
             'font_color': '#000000'})
        header_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'center', 'valign': 'vcenter', 'bg_color': '#00003e', 'font_color': '#FFFFFF', 'text_wrap': True})
        footer_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'center', 'valign': 'vcenter', 'bg_color': '#00003e', 'font_color': '#FFFFFF', 'text_wrap': True,
             'border': False})
        text_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        number_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right',
             'num_format': '#,##0_);[Red](#,##0);- ;@'})
        number_format = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right',
             'num_format': '#,##0.00_);[Red](#,##0.00);-  ;@'})
        total_qty = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'bold': True,
             'align': 'right', 'num_format': '#,##0_);', 'bg_color': '#00003e',
             'font_color': '#FFFFFF'})
        total_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'bold': True,
             'align': 'right', 'num_format': '#,##0.00_);', 'bg_color': '#00003e',
             'font_color': '#FFFFFF'})
        quantity_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'bold': True,
             'align': 'right', 'num_format': '#,##0_);[Red](#,##0);-  ;@', 'bg_color': '#00003e',
             'font_color': '#FFFFFF'})
        percent_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'bold': True,
             'align': 'right', 'num_format': '0.0%', 'bg_color': '#00003e',
             'font_color': '#FFFFFF'})
        date_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right',
             'num_format': 'YYYY-MM-DD'})
        semi_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'center', 'valign': 'vcenter', 'font_color': 'black', 'text_wrap': True,
             'num_format': 'd mmm yyyy'
             })
        percent_format = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right',
             'num_format': '0.0%'})

        if wizard.report_filter == 'sales_cash':
            if wizard.branch_filter:
                branches = wizard.branch_filter
                # search for all branches allowed for the user
            else:
                cash_branch_ids = list(
                    set(wizard.env['sales.cash'].search([('amount', '>', 0.0), ('date', '>=', wizard.date_from),
                                                         ('date', '<=', wizard.date_to)]).mapped('branch_id')))

                branches = request.env['res.branch'].search(
                    [('code', 'in', cash_branch_ids)])

            branches_totals = {}
            # loop all selected branches
            for branch in branches:
                # create worksheet/tab per branch
                sheet = workbook.add_worksheet(branch.name)

                # set the orientation to landscape
                sheet.set_landscape()
                # set up the paper size, 9 means A4
                sheet.set_paper(9)
                # set up the margin in inch
                sheet.set_margins(0.5, 0.5, 0.5, 0.5)

                # set up the column width
                sheet.set_column('A:A', 20)
                sheet.set_column('B:V', 25)

                title_report = 'SALES CASH REPORT'
                sheet_name = branch.name

                sheet.merge_range('A1:R1', title_report, branch_title_style)
                sheet.merge_range('A2:R2', sheet_name, branch_title_style)
                sheet.merge_range('A3:R3', "from ({dateFrom}) to ({dateTo})".format(
                    dateFrom=default_date_format(wizard.date_from),
                    dateTo=default_date_format(wizard.date_to), ), branch_title_style)

                sheet.write(3, 0, 'SALES TEAM', header_style)
                sheet.write(3, 1, 'ORDER DATE', header_style)
                sheet.write(3, 2, 'SALES PERSON', header_style)
                sheet.write(3, 3, 'SALES ORDER NO.', header_style)
                sheet.write(3, 4, 'CUSTOMER', header_style)
                sheet.write(3, 5, 'CLASSIFICATION', header_style)
                sheet.write(3, 6, 'BRAND', header_style)
                sheet.write(3, 7, 'BARCODE', header_style)
                sheet.write(3, 8, 'DESCRIPTION', header_style)
                sheet.write(3, 9, 'ENGINE NO.', header_style)
                sheet.write(3, 10, 'CHASSIS NO.', header_style)
                sheet.write(3, 11, 'PRICE LIST', header_style)
                sheet.write(3, 12, 'TAGS', header_style)
                sheet.write(3, 13, 'PAYMENT TERM', header_style)
                sheet.write(3, 14, 'QUANTITY', header_style)
                sheet.write(3, 15, 'COST', header_style)
                sheet.write(3, 16, 'AMOUNT', header_style)
                sheet.write(3, 17, 'COMPANY', header_style)
                sheet.write(3, 18, 'INVOICE NAME', header_style)
                sheet.write(3, 19, 'INVOICE SLIP', header_style)
                sheet.write(3, 20, 'INVOICE DATE', header_style)
                sheet.write(3, 21, 'INVOICE STATUS', header_style)

                row = 4
                number = 5

                sheet.autofilter("A4:V%s" % row)

                sales_branch = request.env['sales.cash'].search(
                    [('amount', '>', 0), ('branch_id', '=', branch.code), ('date', '>=', wizard.date_from),
                     ('date', '<=', wizard.date_to)], order='date')

                for sales_b in sales_branch:
                    sheet.write(row, 0, sales_b.salesteam, text_style)
                    sheet.write(row, 1, str(sales_b.date), text_style)
                    sheet.write(row, 2, sales_b.salesperson, text_style)
                    sheet.write(row, 3, sales_b.so_number, number_style)
                    sheet.write(row, 4, sales_b.customer, text_style)
                    sheet.write(row, 5, sales_b.product_category, text_style)
                    sheet.write(row, 6, sales_b.brand, text_style)
                    sheet.write(row, 7, sales_b.barcode, text_style)
                    sheet.write(row, 8, sales_b.standard_description, number_style)
                    sheet.write(row, 9, sales_b.engine_number, text_style)
                    sheet.write(row, 10, sales_b.chassis_number, text_style)
                    sheet.write(row, 11, sales_b.pricelist, text_style)
                    sheet.write(row, 12, sales_b.tags, text_style)
                    sheet.write(row, 13, sales_b.payment_term, text_style)
                    sheet.write(row, 14, sales_b.qty, number_style)
                    sheet.write(row, 15, sales_b.cost, number_style)
                    sheet.write(row, 16, sales_b.amount, number_style)
                    sheet.write(row, 17, sales_b.company, text_style)
                    sheet.write(row, 18, sales_b.invoice_name, text_style)
                    sheet.write(row, 19, sales_b.invoice_slip, text_style)
                    sheet.write(row, 20, sales_b.invoice_date, text_style)
                    sheet.write(row, 21, sales_b.invoice_state, text_style)

                    row += 1

                if not sales_branch:
                    # the report content will be in a blank row
                    sheet.write(row, 0, '', text_style)
                    sheet.write(row, 1, 'Nothing to Print', text_style)
                    sheet.write(row, 2, '', text_style)
                    sheet.write(row, 3, '', text_style)
                    sheet.write(row, 4, '', text_style)
                    sheet.write(row, 5, '', text_style)
                    sheet.write(row, 6, '', text_style)
                    sheet.write(row, 7, '', text_style)
                    sheet.write(row, 8, '', text_style)
                    sheet.write(row, 9, '', text_style)
                    sheet.write(row, 10, '', text_style)
                    sheet.write(row, 11, '', text_style)
                    sheet.write(row, 12, '', text_style)
                    sheet.write(row, 13, '', number_style)
                    sheet.write(row, 14, '', number_format)
                    sheet.write(row, 15, '', number_format)
                    sheet.write(row, 16, '', text_style)
                    sheet.write(row, 17, '', text_style)
                    sheet.write(row, 18, '', text_style)
                    sheet.write(row, 19, '', text_style)
                    sheet.write(row, 20, '', text_style)
                    sheet.write(row, 21, '', text_style)

                    row += 1

                sheet.write(row, 0, '', footer_style)
                sheet.write(row, 1, '', footer_style)
                sheet.write(row, 2, '', footer_style)
                sheet.write(row, 3, '', footer_style)
                sheet.write(row, 4, '', footer_style)
                sheet.write(row, 5, '', footer_style)
                sheet.write(row, 6, '', footer_style)
                sheet.write(row, 7, '', footer_style)
                sheet.write(row, 8, '', footer_style)
                sheet.write(row, 9, '', footer_style)
                sheet.write(row, 10, '', footer_style)
                sheet.write(row, 11, '', footer_style)
                sheet.write(row, 12, '', footer_style)
                sheet.write(row, 13, 'TOTAL:', footer_style)
                sheet.write(row, 14, '=SUBTOTAL(109,$O$5:$O$%s)' % row, total_qty)
                sheet.write(row, 15, '=SUBTOTAL(109,$P$5:$P$%s)' % row, total_style)
                sheet.write(row, 16, '=SUBTOTAL(109,$Q$5:$Q$%s)' % row, total_style)
                sheet.write(row, 17, '', footer_style)
                sheet.write(row, 18, '', footer_style)
                sheet.write(row, 19, '', footer_style)
                sheet.write(row, 20, '', footer_style)
                sheet.write(row, 21, '', footer_style)

                row += 1

        elif wizard.report_filter == 'sales_credit':
            if wizard.branch_filter:
                branches = wizard.branch_filter
                # search for all branches allowed for the user
            else:
                credit_branch_ids = list(
                    set(wizard.env['sales.credit'].search([('amount', '>', 0.0), ('date', '>=', wizard.date_from),
                                                           ('date', '<=', wizard.date_to)]).mapped('branch_id')))

                branches = request.env['res.branch'].search(
                    [('code', 'in', credit_branch_ids)])

            branches_totals = {}
            # loop all selected branches
            for branch in branches:
                # create worksheet/tab per branch
                sheet = workbook.add_worksheet(branch.name)

                # set the orientation to landscape
                sheet.set_landscape()
                # set up the paper size, 9 means A4
                sheet.set_paper(9)
                # set up the margin in inch
                sheet.set_margins(0.5, 0.5, 0.5, 0.5)

                # set up the column width
                sheet.set_column('A:A', 20)
                sheet.set_column('B:V', 25)

                title_report = 'SALES CREDIT REPORT'
                sheet_name = branch.name

                sheet.merge_range('A1:R1', title_report, branch_title_style)
                sheet.merge_range('A2:R2', sheet_name, branch_title_style)
                sheet.merge_range('A3:R3', "from ({dateFrom}) to ({dateTo})".format(
                    dateFrom=default_date_format(wizard.date_from),
                    dateTo=default_date_format(wizard.date_to), ), branch_title_style)

                sheet.write(3, 0, 'SALES TEAM', header_style)
                sheet.write(3, 1, 'ORDER DATE', header_style)
                sheet.write(3, 2, 'SALES PERSON', header_style)
                sheet.write(3, 3, 'SALES ORDER NO.', header_style)
                sheet.write(3, 4, 'CUSTOMER', header_style)
                sheet.write(3, 5, 'CLASSIFICATION', header_style)
                sheet.write(3, 6, 'BRAND', header_style)
                sheet.write(3, 7, 'BARCODE', header_style)
                sheet.write(3, 8, 'DESCRIPTION', header_style)
                sheet.write(3, 9, 'ENGINE NO.', header_style)
                sheet.write(3, 10, 'CHASSIS NO.', header_style)
                sheet.write(3, 11, 'PRICE LIST', header_style)
                sheet.write(3, 12, 'TAGS', header_style)
                sheet.write(3, 13, 'PAYMENT TERM', header_style)
                sheet.write(3, 14, 'QUANTITY', header_style)
                sheet.write(3, 15, 'COST', header_style)
                sheet.write(3, 16, 'AMOUNT', header_style)
                sheet.write(3, 17, 'COMPANY', header_style)
                sheet.write(3, 18, 'INVOICE NAME', header_style)
                sheet.write(3, 19, 'INVOICE SLIP', header_style)
                sheet.write(3, 20, 'INVOICE DATE', header_style)
                sheet.write(3, 21, 'INVOICE STATUS', header_style)

                row = 4
                number = 5

                sheet.autofilter("A4:V%s" % row)

                sales_branch = request.env['sales.credit'].search(
                    [('amount', '>', 0), ('branch_id', '=', branch.code), ('date', '>=', wizard.date_from),
                     ('date', '<=', wizard.date_to)], order='date')

                for sales_b in sales_branch:
                    sheet.write(row, 0, sales_b.salesteam, text_style)
                    sheet.write(row, 1, str(sales_b.date), text_style)
                    sheet.write(row, 2, sales_b.salesperson, text_style)
                    sheet.write(row, 3, sales_b.so_number, number_style)
                    sheet.write(row, 4, sales_b.customer, text_style)
                    sheet.write(row, 5, sales_b.product_category, text_style)
                    sheet.write(row, 6, sales_b.brand, text_style)
                    sheet.write(row, 7, sales_b.barcode, text_style)
                    sheet.write(row, 8, sales_b.standard_description, number_style)
                    sheet.write(row, 9, sales_b.engine_number, text_style)
                    sheet.write(row, 10, sales_b.chassis_number, text_style)
                    sheet.write(row, 11, sales_b.pricelist, text_style)
                    sheet.write(row, 12, sales_b.tags, text_style)
                    sheet.write(row, 13, sales_b.payment_term, text_style)
                    sheet.write(row, 14, sales_b.qty, number_style)
                    sheet.write(row, 15, sales_b.cost, number_style)
                    sheet.write(row, 16, sales_b.amount, number_style)
                    sheet.write(row, 17, sales_b.company, text_style)
                    sheet.write(row, 18, sales_b.invoice_name, text_style)
                    sheet.write(row, 19, sales_b.invoice_slip, text_style)
                    sheet.write(row, 20, sales_b.invoice_date, text_style)
                    sheet.write(row, 21, sales_b.invoice_state, text_style)

                    row += 1

                if not sales_branch:
                    # the report content will be in a blank row
                    sheet.write(row, 0, '', text_style)
                    sheet.write(row, 1, 'Nothing to Print', text_style)
                    sheet.write(row, 2, '', text_style)
                    sheet.write(row, 3, '', text_style)
                    sheet.write(row, 4, '', text_style)
                    sheet.write(row, 5, '', text_style)
                    sheet.write(row, 6, '', text_style)
                    sheet.write(row, 7, '', text_style)
                    sheet.write(row, 8, '', text_style)
                    sheet.write(row, 9, '', text_style)
                    sheet.write(row, 10, '', text_style)
                    sheet.write(row, 11, '', text_style)
                    sheet.write(row, 12, '', text_style)
                    sheet.write(row, 13, '', number_style)
                    sheet.write(row, 14, '', number_format)
                    sheet.write(row, 15, '', number_format)
                    sheet.write(row, 16, '', text_style)
                    sheet.write(row, 17, '', text_style)
                    sheet.write(row, 18, '', text_style)
                    sheet.write(row, 19, '', text_style)
                    sheet.write(row, 20, '', text_style)
                    sheet.write(row, 21, '', text_style)

                    row += 1

                sheet.write(row, 0, '', footer_style)
                sheet.write(row, 1, '', footer_style)
                sheet.write(row, 2, '', footer_style)
                sheet.write(row, 3, '', footer_style)
                sheet.write(row, 4, '', footer_style)
                sheet.write(row, 5, '', footer_style)
                sheet.write(row, 6, '', footer_style)
                sheet.write(row, 7, '', footer_style)
                sheet.write(row, 8, '', footer_style)
                sheet.write(row, 9, '', footer_style)
                sheet.write(row, 10, '', footer_style)
                sheet.write(row, 11, '', footer_style)
                sheet.write(row, 12, '', footer_style)
                sheet.write(row, 13, 'TOTAL:', footer_style)
                sheet.write(row, 14, '=SUBTOTAL(109,$O$5:$O$%s)' % row, total_qty)
                sheet.write(row, 15, '=SUBTOTAL(109,$P$5:$P$%s)' % row, total_style)
                sheet.write(row, 16, '=SUBTOTAL(109,$Q$5:$Q$%s)' % row, total_style)
                sheet.write(row, 17, '', footer_style)
                sheet.write(row, 18, '', footer_style)
                sheet.write(row, 19, '', footer_style)
                sheet.write(row, 20, '', footer_style)
                sheet.write(row, 21, '', footer_style)
                row += 1

        elif wizard.report_filter == 'sales_summary':
            if wizard.branch_filter:
                branches = wizard.branch_filter
                # search for all branches allowed for the user
            else:
                summary_branch_ids = list(
                    set(wizard.env['sales.summary'].search([('amount', '>', 0), ('date', '>=', wizard.date_from),
                                                           ('date', '<=', wizard.date_to)]).mapped('branch_id')))

                branches = request.env['res.branch'].search(
                    [('code', 'in', summary_branch_ids)])

            branches_totals = {}
            for branch in branches:
                # create worksheet/tab per branch
                sheet = workbook.add_worksheet(branch.name)

                # set the orientation to landscape
                sheet.set_landscape()
                # set up the paper size, 9 means A4
                sheet.set_paper(9)
                # set up the margin in inch
                sheet.set_margins(0.5, 0.5, 0.5, 0.5)

                # set up the column width
                sheet.set_column('A:A', 20)
                sheet.set_column('B:U', 25)

                title_report = 'SALES SUMMARY REPORT'
                sheet_name = branch.name

                sheet.merge_range('A1:Q1', title_report, branch_title_style)
                sheet.merge_range('A2:Q2', sheet_name, branch_title_style)
                sheet.merge_range('A3:Q3', "from ({dateFrom}) to ({dateTo})".format(
                    dateFrom=default_date_format(wizard.date_from),
                    dateTo=default_date_format(wizard.date_to), ), branch_title_style)

                sheet.write(3, 0, 'ORDER DATE', header_style)
                sheet.write(3, 1, 'SALES ORDER NO.', header_style)
                sheet.write(3, 2, 'AREA', header_style)
                sheet.write(3, 3, 'BRANCH.', header_style)
                sheet.write(3, 4, 'BARCODE', header_style)
                sheet.write(3, 5, 'BRAND', header_style)
                sheet.write(3, 6, 'CLASSIFICATION', header_style)
                sheet.write(3, 7, 'DESCRIPTION', header_style)
                sheet.write(3, 8, 'CUSTOMER', header_style)
                sheet.write(3, 9, 'ENGINE NO.', header_style)
                sheet.write(3, 10, 'CHASSIS NO.', header_style)
                sheet.write(3, 11, 'PAYMENT TERM', header_style)
                sheet.write(3, 12, 'PRICE LIST', header_style)
                sheet.write(3, 13, 'QUANTITY', header_style)
                sheet.write(3, 14, 'COST', header_style)
                sheet.write(3, 15, 'AMOUNT', header_style)
                sheet.write(3, 16, 'COMPANY', header_style)
                sheet.write(3, 17, 'INVOICE NAME', header_style)
                sheet.write(3, 18, 'INVOICE SLIP', header_style)
                sheet.write(3, 19, 'INVOICE DATE', header_style)
                sheet.write(3, 20, 'INVOICE STATUS', header_style)

                row = 4

                sheet.autofilter("A4:U%s" % row)

                sales_branch = request.env['sales.summary'].search(
                    [('amount', '>', 0), ('branch_id', '=', branch.code), ('date', '>=', wizard.date_from),
                     ('date', '<=', wizard.date_to)], order='date')

                for sales_b in sales_branch:
                    sheet.write(row, 0, str(sales_b.date), text_style)
                    sheet.write(row, 1, sales_b.so_number, text_style)
                    sheet.write(row, 2, sales_b.area, text_style)
                    sheet.write(row, 3, sales_b.branch, text_style)
                    sheet.write(row, 4, sales_b.barcode, text_style)
                    sheet.write(row, 5, sales_b.brand, text_style)
                    sheet.write(row, 6, sales_b.product_category, text_style)
                    sheet.write(row, 7, sales_b.standard_description, number_style)
                    sheet.write(row, 8, sales_b.customer, text_style)
                    sheet.write(row, 9, sales_b.engine_number, text_style)
                    sheet.write(row, 10, sales_b.chassis_number, text_style)
                    sheet.write(row, 11, sales_b.payment_term, text_style)
                    sheet.write(row, 12, sales_b.pricelist, text_style)
                    sheet.write(row, 13, sales_b.qty, number_style)
                    sheet.write(row, 14, sales_b.cost, number_style)
                    sheet.write(row, 15, sales_b.amount, number_style)
                    sheet.write(row, 16, sales_b.company, text_style)
                    sheet.write(row, 17, sales_b.invoice_name, text_style)
                    sheet.write(row, 18, sales_b.invoice_slip, text_style)
                    sheet.write(row, 19, sales_b.invoice_date, text_style)
                    sheet.write(row, 20, sales_b.invoice_state, text_style)

                    row += 1

                    # branches without stock transfer records found
                if not sales_branch:
                    # the report content will be in a blank row
                    sheet.write(row, 0, '', text_style)
                    sheet.write(row, 1, 'Nothing to Print', text_style)
                    sheet.write(row, 2, '', text_style)
                    sheet.write(row, 3, '', text_style)
                    sheet.write(row, 4, '', text_style)
                    sheet.write(row, 5, '', text_style)
                    sheet.write(row, 6, '', text_style)
                    sheet.write(row, 7, '', text_style)
                    sheet.write(row, 8, '', text_style)
                    sheet.write(row, 9, '', text_style)
                    sheet.write(row, 10, '', text_style)
                    sheet.write(row, 11, '', text_style)
                    sheet.write(row, 12, '', text_style)
                    sheet.write(row, 13, '', number_style)
                    sheet.write(row, 14, '', number_format)
                    sheet.write(row, 15, '', number_format)
                    sheet.write(row, 16, '', text_style)
                    sheet.write(row, 17, '', text_style)
                    sheet.write(row, 18, '', text_style)
                    sheet.write(row, 19, '', text_style)
                    sheet.write(row, 20, '', text_style)

                    row += 1

                sheet.write(row, 0, '', footer_style)
                sheet.write(row, 1, '', footer_style)
                sheet.write(row, 2, '', footer_style)
                sheet.write(row, 3, '', footer_style)
                sheet.write(row, 4, '', footer_style)
                sheet.write(row, 5, '', footer_style)
                sheet.write(row, 6, '', footer_style)
                sheet.write(row, 7, '', footer_style)
                sheet.write(row, 8, '', footer_style)
                sheet.write(row, 9, '', footer_style)
                sheet.write(row, 10, '', footer_style)
                sheet.write(row, 11, '', footer_style)
                sheet.write(row, 12, 'TOTAL:', footer_style)
                sheet.write(row, 13, '=SUBTOTAL(109,$N$5:$N$%s)' % row, total_qty)
                sheet.write(row, 14, '=SUBTOTAL(109,$O$5:$O$%s)' % row, total_style)
                sheet.write(row, 15, '=SUBTOTAL(109,$P$5:$P$%s)' % row, total_style)
                sheet.write(row, 16, '', footer_style)
                sheet.write(row, 17, '', footer_style)
                sheet.write(row, 18, '', footer_style)
                sheet.write(row, 19, '', footer_style)
                sheet.write(row, 20, '', footer_style)

                row += 1
        # if branch.name not in branches_totals:
        #     branches_totals[branch.name] = row + 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
