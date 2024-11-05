# -*- coding: utf-8 -*-
import psycopg2
from odoo import http, models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from datetime import date, datetime, timedelta
import calendar
from xlsxwriter.utility import xl_col_to_name
import datetime

SAT = 5; SUN = 6

class ActualvsTargetReportController(http.Controller):
    @http.route([
        '/sales_dashboard/get_sales_dashboard_excel_report/<model("sales.wizard"):wizard>',
    ], type='http', auth="user", csrf=False)
    def get_sales_dashboard_excel_report(self, wizard=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition',
                 content_disposition('Sales Performance Report: Actual Vs Target' + str(wizard.end_date) + '.xlsx'))
            ]
        )

        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 14, 'bold': True, 'align': 'center', 'num_format': 'd mmm yyyy'})
        header_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'center', 'valign': 'vcenter', 'bg_color': '#00003e', 'font_color': '#FFFFFF', 'text_wrap': True,
             'num_format': 'd mmm yyyy'
             })
        text_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left',
             'num_format': 'MM/DD/YYYY'})
        number_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right',
             'num_format': '#,##0_);[Red](#,##0);-  ;@'})
        value_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right',
             'num_format': '#,##0.00_);[Red](#,##0.00);-  ;@'})
        total_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'bold': True,
             'align': 'right', 'num_format': '#,##0.00_);[Red](#,##0.00);-  ;@', 'bg_color': '#00003e',
             'font_color': '#FFFFFF'})
        total1_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 10, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'bold': True,
             'align': 'right', 'num_format': '#,##0.00_);[Red](#,##0.00);-  ;@', 'bg_color': '#FF0000',
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

        # create Actual vs Target sheet
        sheet = workbook.add_worksheet('Monthly As of ' + str(wizard.end_date))
        # set the orientation to landscape
        sheet.set_landscape()
        # set up the paper size, 9 means A4
        sheet.set_paper(9)
        # set up the margin in inch
        sheet.set_margins(0.5, 0.5, 0.5, 0.5)

        # set up the column width
        sheet.set_column('A:A', 25)
        sheet.set_column('B:F', 15)
        sheet.set_column('G:G', 10)
        sheet.set_column('H:H', 23)
        sheet.set_column('I:M', 15)
        sheet.set_column('L:L', 10)
        sheet.merge_range('A1:M1', 'Sales Performance : Actual vs Target', title_style)

        # Excel box
        fill_box = '■'
        blank_box = '□'

        # generate Excel file based on wizard's inputs
        wizard.with_context(for_excel=True).generate_tree_view()

        row = 1
        # by time series
        sheet.write(row, 0, 'TIME SERIES', header_style)
        # time series: weekly
        if wizard.time_series == 'week':
            week_box = fill_box
        else:
            week_box = blank_box
        # time series: monthly
        if wizard.time_series == 'month':
            month_box = fill_box
        else:
            month_box = blank_box
        row += 1
        sheet.write(row, 0, week_box + 'Weekly', text_style)
        row += 1
        sheet.write(row, 0, month_box + 'Monthly', text_style)

        # by product
        row += 1
        sheet.write(row, 0, 'BY PRODUCT', header_style)
        row += 1
        # search all products sold
        product = wizard.env['sales.list'].search([('grp', '!=', False)])
        # search all products listed
        descriptions = wizard.env['sales.description'].search([('id', '!=', 0)])
        # group and filter by product
        if wizard.criteria == 'standard_description' and wizard.description_ids:
            # loop all products in groups
            for prod in product:
                # fill box with products through 'group by'
                if prod.wizard2_id:
                    des_box = fill_box
                    row += 1
                    sheet.write(row, 0, des_box + prod.grp, text_style)
        # filter by product
        elif wizard.description_ids:
            # loop all product descriptions
            for descript in descriptions:
                # fill box with selected product descriptions
                if descript in wizard.description_ids:
                    des_box = fill_box
                    row += 1
                    sheet.write(row, 0, des_box + descript.description_name, text_style)
        else:
            des_box = fill_box  # Fill box with all product descriptions
            sheet.write(row, 0, des_box + 'All Products', text_style)

        # by product group
        row += 1
        sheet.write(row, 0, 'BY PRODUCT GROUP', header_style)
        row += 1
        # search all products group from actual sales
        sales_list = wizard.env['sales.list'].search([('grp', '!=', False)])
        # search all product groups listed
        category = wizard.env['sales.category'].search([('categ_name', '!=', False)])
        # group and filter by product group
        if wizard.criteria == 'product_category' and wizard.category_ids:
            # loop all product groups in groups
            for sales in sales_list:
                # fill box with product groups through 'group by'
                if sales.wizard2_id:
                    sales_box = fill_box
                    row += 1
                    sheet.write(row, 0, sales_box + sales.grp, text_style)
        # filter by product group
        elif wizard.category_ids:
            # loop all product groups
            for descript in category:
                if descript in wizard.category_ids:
                    des_box = fill_box
                    row += 1
                    sheet.write(row, 0, des_box + descript.categ_name, text_style)
        else:
            bran_box = fill_box  # Fill box with all product brands
            sheet.write(row, 0, bran_box + 'All Product Groups', text_style)

        # by brand
        row += 2
        sheet.write(row, 0, 'BY BRAND', header_style)
        row += 1
        # search all brands from actual sales
        listing = wizard.env['sales.list'].search([('grp', '!=', False)])
        # search all brands listed
        branding = wizard.env['sales.brand'].search([('brand_name', '!=', False)])
        # group and filter by brand
        if wizard.criteria == 'brand' and wizard.brand_ids:
            # loop all brands in groups
            for lists in listing:
                # fill box with brands through 'group by'
                if lists.wizard2_id:
                    bran_box = fill_box
                    row += 1
                    sheet.write(row, 0, bran_box + lists.grp, text_style)
        # filter by brand
        elif wizard.brand_ids:
            # loop all brands
            for brand in branding:
                if brand in wizard.brand_ids:
                    bran_box = fill_box
                    row += 1
                    sheet.write(row, 0, bran_box + brand.brand_name, text_style)
        else:
            bran_box = fill_box  # Fill box with all product brands
            sheet.write(row, 0, bran_box + 'All Brands', text_style)

        # by branch
        row += 1
        sheet.write(row, 0, 'BY BRANCH', header_style)
        row += 1
        # search all branches from actual sales
        listing = wizard.env['sales.list'].search([('grp', '!=', False)])
        # search all branches listed
        branches = wizard.env['sales.branch'].search([('branch_name', '!=', False)])
        # group and filter by branch
        if wizard.criteria == 'branch' and wizard.branch_ids:
            # loop all brands in groups
            for lists in listing:
                # fill box with branches through 'group by'
                if lists.wizard2_id:
                    bran_box = fill_box
                    row += 1
                    sheet.write(row, 0, bran_box + lists.grp, text_style)
        # filter by branch
        elif wizard.branch_ids:
            # loop all branches
            for branch in branches:
                if branch in wizard.branch_ids:
                    bran_box = fill_box
                    row += 1
                    sheet.write(row, 0, bran_box + branch.branch_name, text_style)
        else:
            bran_box = fill_box     # Fill box with all branches
            sheet.write(row, 0, bran_box + 'All Branches', text_style)

        # by area
        row += 1
        sheet.write(row, 0, 'BY AREA', header_style)
        row += 1
        # search all areas from actual sales
        area = wizard.env['sales.list'].search([('grp', '!=', False)])
        # search all areas listed
        areas = wizard.env['sales.area'].search([('id', '!=', 0)], order="area_name")
        # group and filter by area
        if wizard.criteria == 'area' and wizard.area_ids:
            # fill box with areas through 'group by'
            for are in area:
                if are.wizard2_id:
                    ar_box = fill_box
                    row += 1
                    sheet.write(row, 0, ar_box + are.grp, text_style)
        # filter by area
        elif wizard.area_ids:
            # loop all areas
            for area in areas:
                if area in wizard.area_ids:
                    ar_box = fill_box
                    row += 1
                    sheet.write(row, 0, ar_box + area.area_name, text_style)
        else:
            bran_box = fill_box      # Fill box with all areas
            sheet.write(row, 0, bran_box + 'All Areas', text_style)

        # by usage
        row += 1
        sheet.write(row, 0, 'BY USAGE', header_style)
        row += 1
        # search all usages listed
        uses = wizard.env['sales.usage'].search([('usage_name', '!=', False)], order="usage_name")
        # search all usages from actual sales
        us = wizard.env['sales.list'].search([('grp', '!=', False)])
        # group and filter by usage
        if wizard.criteria == 'usage' and wizard.usage_ids:
            # fill box with areas through 'group by'
            for u in us:
                if u.wizard2_id:
                    us_box = fill_box
                    row += 1
                    sheet.write(row, 0, us_box + u.grp, text_style)
        # filter by usage
        elif wizard.usage_ids:
            # loop all usages
            for ese in uses:
                if ese in wizard.usage_ids:
                    us_box = fill_box
                    row += 1
                    sheet.write(row, 0, us_box + ese.usage_name, text_style)
        else:
            bran_box = fill_box      # Fill box with all areas
            sheet.write(row, 0, bran_box + 'All Usage', text_style)

        # by sales type
        row += 1
        sheet.write(row, 0, 'SALES TYPE', header_style)
        # search all sales types listed
        sales_type = wizard.env['sales.type'].search([('type_name', '!=', False)], order="type_name")
        # loop all sales types
        for types in sales_type:
            ty_box = blank_box
            if types in wizard.type_ids:
                ty_box = fill_box
            row += 1
            sheet.write(row, 0, ty_box + types.type_name, text_style)

        # Unit of measure
        length1 = 2
        sheet.merge_range('B2:C2', 'UNIT OF MEASURE', header_style)
        # value based columns
        if wizard.unit_of_measure == 'value':
            value_box = fill_box
        else:
            value_box = blank_box
        # quantity based columns
        if wizard.unit_of_measure == 'quantity':
            quantity_box = fill_box
        else:
            quantity_box = blank_box
        row += 1
        sheet.merge_range('B3:C3', value_box + ' Value', text_style)
        row += 1
        sheet.merge_range('B4:C4', quantity_box + ' Quantity', text_style)

        # Row for Sales Category
        row = 1
        sheet.merge_range('D2:F2', 'SALES CATEGORY', header_style)
        # gross sales
        if wizard.category_sales == 'gross sales':
            gross_box = fill_box
        else:
            gross_box = blank_box
        # return sales
        if wizard.category_sales == 'return sales':
            return_box = fill_box
        else:
            return_box = blank_box
        # discount sales
        if wizard.category_sales == 'discount sales':
            discount_box = fill_box
        else:
            discount_box = blank_box
        # net sales
        if wizard.category_sales == 'net sales':
            net_box = fill_box
        else:
            net_box = blank_box
        sheet.merge_range('D3:F3', gross_box + ' Gross Sales', text_style)
        sheet.merge_range('D4:F4', return_box + ' Return Sales', text_style)
        sheet.merge_range('D5:F5', discount_box + ' Discount Sales', text_style)
        sheet.merge_range('D6:F6', net_box + ' Net Sales', text_style)
        length2 = 4

        # by class outlet
        row = 1
        sheet.merge_range('G2:H2', 'CLASS OUTLET', header_style)
        # search all class outlets listed
        sales_outlet = wizard.env['sales.outlet'].search([('outlet_name', '!=', False)], order="outlet_name")
        length3 = 0
        # loop all class outlets
        for outlet in sales_outlet:
            # fetch selected class outlets
            if outlet.outlet_name:
                length3 += 1
                out_box = blank_box
                # fetch all class outlets
                if outlet in wizard.outlet_ids:
                    out_box = fill_box
                sheet.merge_range('G%s:H%s' % (row, row), out_box + outlet.outlet_name, text_style)

        # Customer type
        row = 1
        sheet.merge_range('I2:K2', 'CUSTOMER TYPE', header_style)
        # search all customer types listed
        sales_customer = wizard.env['sales.customer'].search([('customer_name', '!=', False)], order="customer_name")
        length4 = 0
        # loop all customer types
        for custom in sales_customer:
            # fetch selected customer types
            if custom.customer_name:
                length4 += 1
                cus_box = blank_box
                # fetch all customer types
                if custom in wizard.customer_ids:
                    cus_box = fill_box
                sheet.merge_range('I%s:K%s' % (row, row), cus_box + custom.customer_name, text_style)

        # by service type
        row = 1
        sheet.merge_range('L2:M2', 'SERVICE TYPE', header_style)
        # search all service types listed
        sales_service = wizard.env['sales.service'].search([('service_name', '!=', False)], order="service_name")
        length5 = 0
        # loop all service types
        for service in sales_service:
            # fetch selected service types
            if service.service_name:
                length5 += 1
                serv_box = blank_box
                # fetch all service types
                if service in wizard.service_ids:
                    serv_box = fill_box
                sheet.merge_range('L%s:M%s' % (row, row), serv_box + service.service_name, text_style)

        # sheet merge
        max_length = max(length1, length2, length3, length4, length5)

        # sheet merge for unit of measure
        if length1 < max_length:
            col = 6
            for x in range(max_length - length1):
                sheet.merge_range('B%s:C%s' % (col + x, col + x), '', text_style)
        # sheet merge for sales category
        if length2 < max_length:
            col = 5
            for x in range(max_length - length2):
                sheet.merge_range('D%s:F%s' % (col + x, col + x), '', text_style)
        # sheet merge for class outlet
        if length3 < max_length:
            col = 4
            for x in range(max_length - length3):
                sheet.merge_range('G%s:H%s' % (col + x, col + x), '', text_style)
        # sheet merge for customer type
        if length4 < max_length:
            col = 4
            for x in range(max_length - length4):
                sheet.merge_range('I%s:K%s' % (col + x, col + x), '', text_style)
        # sheet merge for service type
        if length5 < max_length:
            col = 4
            for x in range(max_length - length5):
                sheet.merge_range('L%s:M%s' % (col + x, col + x), '', text_style)

        row = max_length + 3
        # Monthly column
        if wizard.time_series == 'month':
            sheet.merge_range(row, 1, row + 1, 1, 'Actual Last Month', semi_style)
            sheet.merge_range(row, 2, row + 1, 2,  'Actual This Month', semi_style)
            sheet.merge_range(row, 3, row + 1, 3, 'Variance vs Last Mo.', semi_style)
            sheet.merge_range(row, 4, row + 1, 4, 'Target This Month', semi_style)
            sheet.merge_range(row, 5, row + 1, 5, 'Variance vs Target', semi_style)
            sheet.merge_range(row, 6, row + 1, 6, '% Actual vs Target', semi_style)
            sheet.merge_range(row, 7, row + 1, 7, 'GROUP BY', semi_style)
            sheet.merge_range(row, 8, row + 1, 8, 'Actual YTD', semi_style)
            sheet.merge_range(row, 9, row + 1, 9, 'Target YTD', semi_style)
            sheet.merge_range(row, 10, row + 1, 10, 'Variance vs Target YTD', semi_style)
            sheet.merge_range(row, 11, row + 1, 11, '% YTD Actual vs Target ', semi_style)
            sheet.merge_range(row, 12, row + 1, 12, 'Actual YTD Last Year', semi_style)
            row += 2

        wizard.with_context(for_excel=True).generate_tree_view()

        if wizard.criteria == 'standard_description':
            usage_query = '''SELECT usage_name from sales_usage 
            ORDER BY (CASE WHEN usage_name != '' THEN 0 ELSE 1 END), usage_name ASC'''
            request.env.cr.execute(usage_query)
            usages = request.env.cr.fetchall()
            total_formula = '='
            for usage in usages:
                sheet.write(row, 1, usage[0] or 'OTHERS', semi_style)
                sheet.write(row, 2, '', semi_style)
                sheet.write(row, 3, '', semi_style)
                sheet.write(row, 4, '', semi_style)
                sheet.write(row, 5, '', semi_style)
                sheet.write(row, 6, '', semi_style)
                sheet.write(row, 7, '', semi_style)
                sheet.write(row, 8, '', semi_style)
                sheet.write(row, 9, '', semi_style)
                sheet.write(row, 10, '', semi_style)
                sheet.write(row, 11, '', semi_style)
                sheet.write(row, 12, '', semi_style)
                row += 1
                # report content in value
                excel_data = request.env['sales.list'].search([('wizard2_id', '=', wizard.id),('grouping','=',usage[0])])
                row_start = row
                for data_excel in excel_data:
                    sheet.write(row, 1,
                                data_excel.actual_last_month_value if wizard.unit_of_measure == 'value'
                                else data_excel.actual_last_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 2,
                                data_excel.actual_this_month_value if wizard.unit_of_measure == 'value'
                                else data_excel.actual_this_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 3, '=C%s-B%s' % (row + 1, row + 1,),
                                value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 4,
                                data_excel.target_this_month_value if wizard.unit_of_measure == 'value'
                                else data_excel.target_this_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 5, '=E%s-C%s' % (row + 1, row + 1,),
                                value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 6, '=IFERROR((C%s / E%s), 0)' % (row + 1, row + 1,), percent_format)
                    sheet.write(row, 7, data_excel.grp if data_excel.grp != '' else 'OTHERS', text_style)
                    sheet.write(row, 8,
                                data_excel.actual_ytd_value if wizard.unit_of_measure == 'value'
                                else data_excel.actual_ytd_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 9,
                                data_excel.target_ytd_value if wizard.unit_of_measure == 'value'
                                else data_excel.target_ytd_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 10, '=J%s-I%s' % (row + 1, row + 1,),
                                value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 11, '=IFERROR((I%s / J%s), 0)' % (row + 1, row + 1,), percent_format)
                    sheet.write(row, 12,
                                data_excel.actual_ytd_last_year_value if wizard.unit_of_measure == 'value'
                                else data_excel.actual_ytd_last_year_qty,
                                value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    row += 1

                sheet.write(row, 1, '=SUBTOTAL(109,$B$%s:$B$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 2, '=SUBTOTAL(109,$C$%s:$C$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 3, '=SUBTOTAL(109,$D$%s:$D$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 4, '=SUBTOTAL(109,$E$%s:$E$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 5, '=SUBTOTAL(109,$F$%s:$F$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 6, '=IFERROR((C%s / E%s), 0)' % (row + 1, row + 1), percent_style)

                sheet.write(row, 7, 'TOTAL of ' + (usage[0] if usage[0] != '' else 'OTHERS'),
                            header_style)
                sheet.write(row, 8, '=SUBTOTAL(109,$I$%s:$I$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 9, '=SUBTOTAL(109,$J$%s:$J$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 10, '=SUBTOTAL(109,$K$%s:$K$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 11, '=IFERROR((I%s / J%s), 0)' % (row + 1, row + 1,), percent_style)
                sheet.write(row, 12, '=SUBTOTAL(109,$M$%s:$M$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                row += 1
                total_formula += """+*%s""" % (row)

            sheet.write(row, 1, total_formula.replace('*', 'B'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 2, total_formula.replace('*', 'C'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 3, total_formula.replace('*', 'D'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 4, total_formula.replace('*', 'E'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 5, total_formula.replace('*', 'F'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 6, '=IFERROR((C%s / E%s), 0)' % (row + 1, row + 1), percent_style)
            sheet.write(row, 7, 'GRAND TOTAL', header_style)
            sheet.write(row, 8, total_formula.replace('*', 'I'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 9, total_formula.replace('*', 'J'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 10, total_formula.replace('*', 'K'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 11, '=IFERROR((I%s / J%s), 0)' % (row + 1, row + 1,), percent_style)
            sheet.write(row, 12, total_formula.replace('*', 'M'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)

            # next groupings

        elif wizard.criteria == 'branch':
            area_query = '''SELECT area_name from sales_area 
                        ORDER BY (CASE WHEN area_name != '' THEN 0 ELSE 1 END), area_name ASC'''
            request.env.cr.execute(area_query)
            areas = request.env.cr.fetchall()
            total_formula = '='
            for area in areas:
                sheet.write(row, 1, area[0] or 'OTHERS', semi_style)
                sheet.write(row, 2, '', semi_style)
                sheet.write(row, 3, '', semi_style)
                sheet.write(row, 4, '', semi_style)
                sheet.write(row, 5, '', semi_style)
                sheet.write(row, 6, '', semi_style)
                sheet.write(row, 7, '', semi_style)
                sheet.write(row, 8, '', semi_style)
                sheet.write(row, 9, '', semi_style)
                sheet.write(row, 10, '', semi_style)
                sheet.write(row, 11, '', semi_style)
                sheet.write(row, 12, '', semi_style)
                row += 1
                # report content in value
                excel_data = request.env['sales.list'].search([('wizard2_id', '=', wizard.id),('grouping','=',area[0])])
                row_start = row
                for data_excel in excel_data:
                    sheet.write(row, 1,
                                data_excel.actual_last_month_value if wizard.unit_of_measure == 'value'
                                else data_excel.actual_last_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 2,
                                data_excel.actual_this_month_value if wizard.unit_of_measure == 'value'
                                else data_excel.actual_this_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 3, '=C%s-B%s' % (row + 1, row + 1,),
                                value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 4,
                                data_excel.target_this_month_value if wizard.unit_of_measure == 'value'
                                else data_excel.target_this_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 5, '=E%s-C%s' % (row + 1, row + 1,), value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 6, '=IFERROR((C%s / E%s), 0)' % (row + 1, row + 1,), percent_format)
                    sheet.write(row, 7, data_excel.grp if data_excel.grp != '' else 'OTHERS', text_style)
                    sheet.write(row, 8,
                                data_excel.actual_ytd_value if wizard.unit_of_measure == 'value'
                                else data_excel.actual_ytd_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 9,
                                data_excel.target_ytd_value if wizard.unit_of_measure == 'value'
                                else data_excel.target_ytd_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 10, '=J%s-I%s' % (row + 1, row + 1,),
                                value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    sheet.write(row, 11, '=IFERROR((I%s / J%s), 0)' % (row + 1, row + 1,), percent_format)
                    sheet.write(row, 12,
                                data_excel.actual_ytd_last_year_value if wizard.unit_of_measure == 'value'
                                else data_excel.actual_ytd_last_year_qty,
                                value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                    row += 1

                sheet.write(row, 1, '=SUBTOTAL(109,$B$%s:$B$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 2, '=SUBTOTAL(109,$C$%s:$C$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 3, '=SUBTOTAL(109,$D$%s:$D$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 4, '=SUBTOTAL(109,$E$%s:$E$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 5, '=SUBTOTAL(109,$F$%s:$F$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 6,'=IFERROR((C%s / E%s), 0)' % (row + 1, row + 1), percent_style)

                sheet.write(row, 7, 'TOTAL of ' + (area[0] if area[0] != '' else 'OTHERS'), header_style)

                sheet.write(row, 8, '=SUBTOTAL(109,$I$%s:$I$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 9, '=SUBTOTAL(109,$J$%s:$J$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 10, '=SUBTOTAL(109,$K$%s:$K$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                sheet.write(row, 11, '=IFERROR((I%s / J%s), 0)' % (row + 1, row + 1,), percent_style)
                sheet.write(row, 12, '=SUBTOTAL(109,$M$%s:$M$%s)' % (row_start + 1, row),
                            total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
                row += 1
                total_formula += """+*%s""" % (row)

            sheet.write(row, 1, total_formula.replace('*', 'B'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 2, total_formula.replace('*', 'C'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 3, total_formula.replace('*', 'D'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 4, total_formula.replace('*', 'E'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 5, total_formula.replace('*', 'F'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 6, '=IFERROR((C%s / E%s), 0)' % (row + 1, row + 1), percent_style)
            sheet.write(row, 7, 'GRAND TOTAL', header_style)
            sheet.write(row, 8, total_formula.replace('*', 'I'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 9, total_formula.replace('*', 'J'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 10, total_formula.replace('*', 'K'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 11, '=IFERROR((I%s / J%s), 0)' % (row + 1, row + 1,), percent_style)
            sheet.write(row, 12, total_formula.replace('*', 'M'), total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)

            # next groupings

        else:
            excel_data = request.env['sales.list'].search([('wizard2_id', '=', wizard.id)])
            for data_excel in excel_data:
                sheet.write(row, 1,
                            data_excel.actual_last_month_value if wizard.unit_of_measure == 'value'
                            else data_excel.actual_last_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                sheet.write(row, 2,
                            data_excel.actual_this_month_value if wizard.unit_of_measure == 'value'
                            else data_excel.actual_this_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                sheet.write(row, 3, '=C%s-B%s' % (row + 1, row + 1,), value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                sheet.write(row, 4,
                            data_excel.target_this_month_value if wizard.unit_of_measure == 'value'
                            else data_excel.target_this_month_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                sheet.write(row, 5, '=E%s-C%s' % (row + 1, row + 1,), value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                sheet.write(row, 6, '=IFERROR((C%s / E%s), 0)' % (row + 1, row + 1,), percent_format)

                sheet.write(row, 7, data_excel.grp if data_excel.grp != '' else 'OTHERS', text_style)
                sheet.write(row, 8,
                            data_excel.actual_ytd_value if wizard.unit_of_measure == 'value'
                            else data_excel.actual_ytd_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                sheet.write(row, 9,
                            data_excel.target_ytd_value if wizard.unit_of_measure == 'value'
                            else data_excel.target_ytd_qty, value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                sheet.write(row, 10, '=J%s-I%s' % (row + 1, row + 1,), value_style if wizard.unit_of_measure == 'value'
                                else number_style)
                sheet.write(row, 11, '=IFERROR((I%s / J%s), 0)' % (row + 1, row + 1,), percent_format)
                sheet.write(row, 12,
                            data_excel.actual_ytd_last_year_value if wizard.unit_of_measure == 'value'
                            else data_excel.actual_ytd_last_year_qty,
                            value_style if wizard.unit_of_measure == 'value'
                            else number_style)
                row += 1
                # next groupings

            sheet.write(row, 1, '=SUBTOTAL(109,$B$9:B%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 2, '=SUBTOTAL(109,$C$9:C%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 3, '=SUBTOTAL(109,$D$9:D%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 4, '=SUBTOTAL(109,$E$9:E%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 5, '=SUBTOTAL(109,$F$9:F%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 6, '=IFERROR((C%s/E%s),0)' % (row + 1, row + 1), percent_style)
            sheet.write(row, 6, '=IFERROR((C%s/E%s),0)' % (row + 1, row + 1), percent_style)
            sheet.write(row, 7, 'TOTAL', header_style)
            sheet.write(row, 8, '=SUBTOTAL(109,$I$9:I%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 9, '=SUBTOTAL(109,$J$9:J%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 10, '=SUBTOTAL(109,$K$9:K%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)
            sheet.write(row, 11, '=IFERROR((I%s/J%s),0)' % (row + 1, row + 1,), percent_style)
            sheet.write(row, 12, '=SUBTOTAL(109,$M$9:M%s)' % row, total_style if wizard.unit_of_measure == 'value'
                            else quantity_style)

        # layout for Weekly sheet
        sheet2 = workbook.add_worksheet('Weekly As of ' + str(wizard.end_date))
        # set the orientation to landscape
        sheet2.set_landscape()
        # set up the paper size, 9 means A4
        sheet.set_paper(9)
        # set up the margin in inch
        sheet2.set_margins(0.5, 0.5, 0.5, 0.5)

        # set up the column width
        sheet2.set_column('A:A', 25)
        sheet2.set_column('B:M', 25)
        sheet2.merge_range('A1:E1', 'Weekly Sales Performance', title_style)

        row2 = 1
        row_start2 = row2

        request.cr.execute('''SELECT line.holiday_date 
                                 FROM public.holiday_non_operation
                                 INNER JOIN public.holiday_non_operation_line AS line 
                                 ON holiday_non_operation.id = line.id
                                 WHERE EXTRACT(dow FROM line.holiday_date) != 0
                                 ORDER BY holiday_non_operation.id ASC''')

        holiday1 = request.cr.fetchall()
        holidays = []
        for holi1 in holiday1:
            holidays.append(holi1[0])

        target_month = int(wizard.end_date.strftime('%m'))
        target_year = int(wizard.end_date.strftime('%Y'))

        mth = calendar.monthcalendar(target_year, target_month)

        # header here... loop the per week
        col = 0
        row2 = 3
        sheet2.merge_range(row2, col, row2 + 1, col, "GROUP BY", header_style)
        col += 1
        cntr = 1
        weekly_results = {}
        for week in mth:
            wk = []
            for day in week:
                if day != 0:
                    dte = '%s-%s-%s' % (target_year, str(target_month).zfill(2), str(day).zfill(2))
                    current_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
                    wk.append(str(current_date))

            weekly_results[tuple(wk)] = wk

            dte = '%s-%s-%s' % (target_year, target_month, min(wk)[8:10])
            start_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
            dte = '%s-%s-%s' % (target_year, target_month, max(wk)[8:10])
            end_date = datetime.datetime.strptime(dte, '%Y-%m-%d')

            results2 = self.get_sales_data(wizard, start_date, end_date)

            for res in results2:
                week_grp = '%s - %s' % (cntr, res[0])

                if week_grp not in weekly_results:
                    weekly_results[week_grp] = (res[1], res[2])

            cntr += 1

            week_start_formatted = start_date.strftime("%B %d")
            week_end_formatted = end_date.strftime("%B %d")

            sheet2.merge_range(row2, col, row2, col + 1, f'{week_start_formatted}-{week_end_formatted}',
                               header_style)
            sheet2.write(row2 + 1, col, "Sales", header_style)
            sheet2.write(row2 + 1, col + 1, "Target", header_style)

            col += 2

        row2 += 2
        excel_data = request.env['sales.list'].search([('wizard2_id', '=', wizard.id)])
        for res in excel_data:

            col = 0
            sheet2.write(row2, col, res.grp, text_style)
            col += 1

            if wizard.unit_of_measure == 'quantity':
                target_for_the_month = res.target_this_month_qty  # get the target for the month
            else:
                target_for_the_month = res.target_this_month_value  # get the target for the month

            remaining_target = target_for_the_month

            dte = '%s-%s-%s' % (target_year, target_month, min(d for d in mth[0] if d != 0))
            start_month_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
            dte = '%s-%s-%s' % (target_year, target_month, max(d for d in mth[len(mth) - 1] if d != 0))
            end_month_date = datetime.datetime.strptime(dte, '%Y-%m-%d')

            weekend_holidays = self.get_weekends(start_month_date, end_month_date, holidays)
            operation_days_for_the_month = max(d for d in mth[len(mth) - 1] if d != 0) - weekend_holidays

            cntr = 1
            for week in mth:
                wk = []
                for day in week:
                    if day != 0:
                        dte = '%s-%s-%s' % (target_year, target_month, day)
                        current_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
                        wk.append(str(current_date))

                weekly_results[tuple(wk)] = wk

                dte = '%s-%s-%s' % (target_year, target_month, min(wk)[8:10])
                start_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
                dte = '%s-%s-%s' % (target_year, target_month, max(wk)[8:10])
                end_date = datetime.datetime.strptime(dte, '%Y-%m-%d')

                week_grp = '%s - %s' % (cntr, res.grp)
                sales_for_the_week = 0
                if week_grp in weekly_results:
                    if wizard.unit_of_measure == 'quantity':
                        sales_for_the_week = int(weekly_results[week_grp][0])
                    else:
                        sales_for_the_week = weekly_results[week_grp][1]

                # get the operation days gamit tong weekend kag holiday
                dte = '%s-%s-%s' % (target_year, target_month, min(d for d in week if d != 0))
                start_week_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
                dte = '%s-%s-%s' % (target_year, target_month, max(d for d in week if d != 0))
                end_week_date = datetime.datetime.strptime(dte, '%Y-%m-%d')

                weekend_holidays = self.get_weekends(start_week_date, end_week_date, holidays)
                operation_days_for_the_week = len([d for d in week if d != 0]) - weekend_holidays

                if cntr == len(mth):
                    target_for_the_week = remaining_target

                    target_fml = '=%s' % (remaining_target)
                else:

                    if wizard.unit_of_measure == 'quantity':
                        target_for_the_week = round(
                            (target_for_the_month / operation_days_for_the_month) * operation_days_for_the_week,
                            0)  # print(target_for_the_week)
                        target_fml = '=round((%s / %s) * %s,0)' % (
                        target_for_the_month, operation_days_for_the_month, operation_days_for_the_week)
                    else:
                        target_for_the_week = (target_for_the_month / operation_days_for_the_month) * operation_days_for_the_week  # print(target_for_the_week)
                        target_fml = '=(%s / %s) * %s' % (
                        target_for_the_month, operation_days_for_the_month, operation_days_for_the_week)

                remaining_target -= target_for_the_week

                sheet2.write(row2, col, sales_for_the_week,value_style if wizard.unit_of_measure == 'value' else number_style)
                sheet2.write(row2, col + 1, target_fml,value_style if wizard.unit_of_measure == 'value' else number_style)
                col += 2
                cntr += 1

            row2 += 1
            sheet2.write(row2, 0, '', header_style)
            col = 0
            col += 1
            print(mth)
            for week in mth:
                xcol = xl_col_to_name(col)
                sheet2.write(row2, col, '=SUBTOTAL(109,$%s$%s:$%s$%s)' % (xcol, row_start2 + 1, xcol, row2),
                             total_style if wizard.unit_of_measure == 'value' else quantity_style)
                xcol = xl_col_to_name(col + 1)
                sheet2.write(row2, col + 1, '=SUBTOTAL(109,$%s$%s:$%s$%s)' % (xcol, row_start2 + 1, xcol, row2),
                             total_style if wizard.unit_of_measure == 'value'
                             else quantity_style)

                col += 2

        # layout for Draft Invoices sheet
        sheet3 = workbook.add_worksheet('Draft Invoices as of ' + str(wizard.end_date))
        # set the orientation to landscape
        sheet3.set_landscape()
        # set up the paper size, 9 means A4
        sheet3.set_paper(1)
        # set up the margin in inch
        sheet3.set_margins(0.5, 0.5, 0.5, 0.5)
        # set up the freeze panes to 2 columns
        sheet3.freeze_panes(2, 0)
        # set up the row height of headers
        sheet3.set_row(1, 30)

        # set up the column width
        sheet3.set_column('A:AB', 25)
        sheet3.set_column('C:D', 10)
        sheet3.set_column('F:F', 15)
        sheet3.set_column('G:G', 30)
        sheet3.set_column('H:J', 15)
        sheet3.set_column('K:K', 35)
        sheet3.set_column('N:O', 15)
        sheet3.set_column('P:Q', 30)
        sheet3.set_column('R:R', 10)
        sheet3.set_column('S:T', 15)
        sheet3.set_column('U:U', 25)
        sheet3.set_column('V:V', 10)
        sheet3.set_column('W:W', 15)
        sheet3.set_column('Y:Y', 15)
        sheet3.set_column('AA:AB', 15)
        sheet3.merge_range('A1:E1', 'Sales with Draft Invoices', title_style)

        # column titles in Sheet 3
        sheet3.write(1, 0, 'Sales Date', header_style)
        sheet3.write(1, 1, 'Salesperson', header_style)
        sheet3.write(1, 2, 'Company', header_style)
        sheet3.write(1, 3, 'Area Code', header_style)
        sheet3.write(1, 4, 'Branch', header_style)
        sheet3.write(1, 5, 'Sales Order Number', header_style)
        sheet3.write(1, 6, 'Customer', header_style)
        sheet3.write(1, 7, 'Barcode', header_style)
        sheet3.write(1, 8, 'Brand', header_style)
        sheet3.write(1, 9, 'Product Group/Category', header_style)
        sheet3.write(1, 10, 'Description', header_style)
        sheet3.write(1, 11, 'Standard Description', header_style)
        sheet3.write(1, 12, 'Model', header_style)
        sheet3.write(1, 13, 'Usage', header_style)
        sheet3.write(1, 14, 'Sales Type', header_style)
        sheet3.write(1, 15, 'Engine Number', header_style)
        sheet3.write(1, 16, 'Chassis Number', header_style)
        sheet3.write(1, 17, 'Order Lines/Quantity', header_style)
        sheet3.write(1, 18, 'Order Lines/Cost', header_style)
        sheet3.write(1, 19, 'Order Lines/Amount', header_style)
        sheet3.write(1, 20, 'Pricelist', header_style)
        sheet3.write(1, 21, 'Payment Term', header_style)
        sheet3.write(1, 22, 'Status', header_style)
        sheet3.write(1, 23, 'Tags', header_style)
        sheet3.write(1, 24, 'Invoices/ Date', header_style)
        sheet3.write(1, 25, 'Invoices/ Name', header_style)
        sheet3.write(1, 26, 'Invoices/ Slip Number', header_style)
        sheet3.write(1, 27, 'Invoice State', header_style)

        row_invoice = 2
        number_invoice = 1

        # autofilter
        sheet3.autofilter("A2:AB%s" % row_invoice)


        # using dblink to fetch data from live database
        conf = request.env['scm.config'].search([('active', '=', True)], limit=1)
        if conf:
            params = {'host': conf.host,
                      'port': conf.port,
                      'dbname': conf.database,
                      'user': conf.user,
                      'password': conf.password}
        db_conf = ' '.join([f"{key}={value}" for key, value in params.items()])
        dbconn = db_conf
        # SQL query to fetch sales with draft invoices
        request.cr.execute(f"""create extension if not exists dblink;
                                select w.order_line_id, w.invoice_line_id, w.date_order, w.salesperson, w.agent_name, 
								w.company, z.area_code as area, w.branch, 
		                        w.so_number, w.invoice_origin, w.partner_id, 
								w.customer, w.product_id, w.barcode, 
								(CASE WHEN w.barcode LIKE 'SC%' THEN 'SIDECAR'
								ELSE w.brand END) as brand, w.product_category, w.rawdesc,
		                        (CASE WHEN w.barcode LIKE 'SC%' THEN 'SIDECAR'
								ELSE y.description END) as standard_description, w.model,
								(CASE WHEN w.barcode LIKE 'SC%' THEN 'SIDECAR'
								ELSE y.usage END) as usage, w.sales_type,
								w.engine_number, w.chassis_number,
								w.qty, (CASE WHEN w.barcode LIKE 'SC%' THEN (w.price_unit/1.15)
								ELSE y.cost END) as cost, w.price_unit, w.amount_total, 
								sum(w.price_unit*w.qty) as gross_sales, w.pricelist, w.payment_term,
								w.status, w.tags,
								w.invoice_id, w.invoice_date, w.inv_name, w.inv_slip, w.invoice_status, z.branch_id
                                from dblink('{dbconn}',
                                'WITH salesperson as (SELECT r.id, s.name from res_users r left join res_partner s
                                    on r.partner_id = s.id),
								sales as (SELECT h.name as company, e.name as branch, c.default_code as barcode,
                                    c.name as rawdesc, c.brand , c.model,
                                    (CASE WHEN c.default_code LIKE ''TR%'' THEN ''TRIMOTOR'' 
									WHEN c.default_code LIKE ''SC%'' THEN ''SIDECAR'' 
									ELSE f.name END) as product_category,
                                    g.name as customer, (CASE WHEN h.name=''EPFC'' THEN ''Installment'' ELSE ''Cash'' END) as sales_type,
                                    b.date_order, b.name as so_number, a.id as so_line_id, b.id as order_id,
                                    b.awb_agent_id, a.qty_invoiced, a.price_unit, a.invoice_status,
                                    a.order_partner_id, b.state as status, a.product_id, a.salesman_id,
									b.pricelist_id, b.payment_term_id, b.awb_lot_id
                                    FROM ((sale_order_line a FULL JOIN sale_order b ON a.order_id = b.id)
                                    FULL JOIN (product_template c FULL JOIN product_product d
                                    ON c.id = d.product_tmpl_id) ON a.product_id = d.id), stock_warehouse e,
                                    product_category f, res_partner g, res_company h
                                    WHERE a.company_id IN (1,2,3) AND b.state IN (''sale'',''done'')
                                    AND b.warehouse_id = e.id AND c.type = ''product'' AND c.tracking IN (''serial'',''lot'',''none'')
                                    AND c.categ_id = f.id AND a.order_partner_id = g.id 
									AND g.name NOT LIKE ''EPFC%'' AND a.company_id = h.id
                                    AND a.invoice_status = ''invoiced'' AND b.invoice_status = ''invoiced''
                                    AND f.name = ''MC'' AND date(b.date_order) <= now()
                                    GROUP BY c.default_code, c.name, c.brand, c.model, e.name, f.name, g.name,
                                    b.name, a.id, b.id, h.name, a.qty_invoiced, a.price_unit, b.date_order, b.awb_agent_id,
                                    a.order_partner_id, a.product_id, a.salesman_id, 
                                    b.pricelist_id, b.payment_term_id, b.awb_lot_id
					                ORDER by b.date_order desc),
				                invoice as (SELECT n.id as invoice_line_id, m.id as invoice_id, m.name as inv_name,
					                m.date as invoice_date, m.inv_slip, m.partner_id, m.invoice_origin, n.quantity, 
					                n.price_unit as amount_total, n.price_unit, n.product_id, m.state
					                from account_move m JOIN account_move_line n on m.id = n.move_id
					                where m.company_id in (1,2,3) and m.state = ''draft'' and m.invoice_origin like ''S%''
					                and m.date is not null
					                and n.parent_state = ''draft'' and n.exclude_from_invoice_tab = false
					                GROUP BY n.id, m.id, m.name, m.date, m.inv_slip, m.partner_id, m.team_id, 
					                m.invoice_origin, n.quantity, n.price_unit, n.product_id, m.state)
				                select coalesce(l.order_line_id, sales.so_line_id) as order_line_id, 
					                coalesce(l.invoice_line_id, invoice.invoice_line_id) as invoice_line_id, 
					                sales.company, sales.branch,
					                coalesce(sales.product_id, invoice.product_id) as product_id,
					                sales.barcode, sales.rawdesc, sales.brand, sales.model, 
					                sales.product_category, sales.customer, sales.sales_type,
					                sales.date_order, sales.so_number, invoice.invoice_origin,
					                k.name as agent_name, invoice.state as invoice_status, invoice.invoice_id, 
					                invoice.inv_name, invoice.inv_slip, 
					                coalesce(invoice.partner_id, sales.order_partner_id) as partner_id,
					                invoice.quantity as qty, invoice.price_unit as price_unit, 
					                invoice.amount_total, sales.status, m.name as tags,
									invoice.invoice_date, salesperson.name as salesperson,
									n.name as pricelist, o.name as payment_term,
									p.name as engine_number, p.chassis_number
					                from sale_order_line_invoice_rel l join sales on sales.so_line_id = l.order_line_id
					                join invoice on l.invoice_line_id = invoice.invoice_line_id 
					                left join res_partner k on k.id = sales.awb_agent_id
					                left join sale_order_tag_rel j on sales.order_id = j.order_id
					                left join crm_tag m on m.id = j.tag_id
									left join salesperson on salesperson.id = sales.salesman_id
									left join account_payment_term o on sales.payment_term_id = o.id
									left join product_pricelist n on sales.pricelist_id = n.id
									left join stock_production_lot p on sales.awb_lot_id = p.id
					                where m.name NOT LIKE ''%INTER BU'' ') 
					            AS w(order_line_id integer, invoice_line_id integer, company varchar, branch varchar, 
					            product_id integer, barcode varchar, rawdesc varchar, brand varchar, model varchar, 
					            product_category varchar, customer varchar,  sales_type varchar, date_order timestamp, 
					            so_number varchar, invoice_origin varchar, agent_name varchar, invoice_status varchar, 
		                        invoice_id integer, inv_name varchar, inv_slip varchar, partner_id varchar, 
		                        qty double precision, price_unit double precision, amount_total double precision, 
		                        status varchar, tags varchar, invoice_date date, salesperson varchar,
								pricelist varchar, payment_term varchar, engine_number varchar, chassis_number varchar)
                                left outer join scm_master_list_mc_data y on y.barcode = w.barcode
	                            left outer join res_area_code z on z.branch_name = w.branch
	                            where date(w.date_order) >= date_trunc('month', DATE '{wizard.end_date}')
                                AND date(w.date_order) <= '{wizard.end_date}'
                                group by w.order_line_id, w.invoice_line_id, w.company, w.branch, z.area_code, 
                                w.product_id, w.barcode, w.rawdesc, y.description, w.brand, w.model, y.usage, 
                                w.product_category, w.customer, w.sales_type, w.date_order, w.so_number, 
                                w.invoice_origin, w.agent_name, w.invoice_date, w.invoice_status, w.invoice_id, 
								w.inv_name, w.inv_slip, w.partner_id, w.qty, w.price_unit, w.salesperson,
								w.amount_total, w.status, w.tags, z.branch_id, w.pricelist, w.payment_term,
								w.engine_number, w.chassis_number, y.cost
                                ORDER BY z.area_code asc, w.company, w.branch, w.date_order desc""")

        dblink_dta = request.cr.fetchall()
        # loop all draft invoices
        for dbl in dblink_dta:
            sheet3.write(row_invoice, 0, str(dbl[2]), text_style)
            sheet3.write(row_invoice, 1, dbl[3], text_style)
            sheet3.write(row_invoice, 2, dbl[5], text_style)
            sheet3.write(row_invoice, 3, dbl[6], text_style)
            sheet3.write(row_invoice, 4, dbl[7], text_style)
            sheet3.write(row_invoice, 5, dbl[8], text_style)
            sheet3.write(row_invoice, 6, dbl[11], text_style)
            sheet3.write(row_invoice, 7, dbl[13], text_style)
            sheet3.write(row_invoice, 8, dbl[14], text_style)
            sheet3.write(row_invoice, 9, dbl[15], text_style)
            sheet3.write(row_invoice, 10, dbl[16], text_style)
            sheet3.write(row_invoice, 11, dbl[17], text_style)
            sheet3.write(row_invoice, 12, dbl[18], text_style)
            sheet3.write(row_invoice, 13, dbl[19], text_style)
            sheet3.write(row_invoice, 14, dbl[20], text_style)
            sheet3.write(row_invoice, 15, dbl[21], text_style)
            sheet3.write(row_invoice, 16, dbl[22], text_style)
            sheet3.write(row_invoice, 17, dbl[23], number_style)
            sheet3.write(row_invoice, 18, dbl[24], value_style)
            sheet3.write(row_invoice, 19, dbl[25], value_style)
            sheet3.write(row_invoice, 20, dbl[28], text_style)
            sheet3.write(row_invoice, 21, dbl[29], text_style)
            sheet3.write(row_invoice, 22, 'Sales Order' if dbl[30] == 'sale' else '', text_style)
            sheet3.write(row_invoice, 23, dbl[31], text_style)
            sheet3.write(row_invoice, 24, str(dbl[33]), text_style)
            sheet3.write(row_invoice, 25, dbl[34], text_style)
            sheet3.write(row_invoice, 26, dbl[35], text_style)
            sheet3.write(row_invoice, 27, 'Draft' if dbl[36] == 'draft' else '', text_style)

            row_invoice += 1
            number_invoice += 1

        sheet3.write(row_invoice, 0, '', header_style)
        sheet3.write(row_invoice, 1, '', header_style)
        sheet3.write(row_invoice, 2, '', header_style)
        sheet3.write(row_invoice, 3, '', header_style)
        sheet3.write(row_invoice, 4, '', header_style)
        sheet3.write(row_invoice, 5, '', header_style)
        sheet3.write(row_invoice, 6, '', header_style)
        sheet3.write(row_invoice, 7, '', header_style)
        sheet3.write(row_invoice, 8, '', header_style)
        sheet3.write(row_invoice, 9, '', header_style)
        sheet3.write(row_invoice, 10, '', header_style)
        sheet3.write(row_invoice, 11, '', header_style)
        sheet3.write(row_invoice, 12, '', header_style)
        sheet3.write(row_invoice, 13, '', header_style)
        sheet3.write(row_invoice, 14, '', header_style)
        sheet3.write(row_invoice, 15, '', header_style)
        sheet3.write(row_invoice, 16, '', header_style)
        sheet3.write(row_invoice, 17, '', header_style)
        sheet3.write(row_invoice, 18, '', header_style)
        sheet3.write(row_invoice, 19, '', header_style)
        sheet3.write(row_invoice, 20, '', header_style)
        sheet3.write(row_invoice, 21, '', header_style)
        sheet3.write(row_invoice, 22, '', header_style)
        sheet3.write(row_invoice, 23, '', header_style)
        sheet3.write(row_invoice, 24, '', header_style)
        sheet3.write(row_invoice, 25, '', header_style)
        sheet3.write(row_invoice, 26, '', header_style)
        sheet3.write(row_invoice, 27, '', header_style)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
    def get_sales_data(self, wizard, start_date, end_date):

        where_cond = ''
        group_by = wizard.criteria

        query2 = f"""WITH sales AS (
                    SELECT
                        {group_by},
                        SUM(qty) as actual_this_week_qty,
                        SUM(amount) as actual_this_week_value
                    FROM
                        sales_summary
                    WHERE
                        date(date) between '{start_date}' and '{end_date}' 
                    GROUP BY
                        {group_by}
                )

                SELECT
                    a.{group_by},
                    a.actual_this_week_qty,
                    a.actual_this_week_value
                FROM
                    sales a
                """

        wizard.env.cr.execute(query2)
        results2 = wizard.env.cr.fetchall()
        print(results2)
        return results2

    def get_weekends(self, start_date, end_date, holidays=None):
        days = [date.fromordinal(d) for d in
                range(start_date.toordinal(),
                      end_date.toordinal() + 1)]

        weekend_days = [d for d in days if d.weekday() == SUN]
        holidays_days = [d for d in days if d in holidays]

        return len(weekend_days) + len(holidays_days)