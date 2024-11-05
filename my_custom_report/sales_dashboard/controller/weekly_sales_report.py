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
import itertools

SAT = 5; SUN = 6

class WeeklyReportsController(http.Controller):
    @http.route([
        '/sales_dashboard/get_weekly_sales_dashboard_excel_report/<model("sales.gm.wizard"):wizard>',
    ], type='http', auth="user", csrf=False)
    def get_weekly_sales_dashboard_excel_report(self, wizard=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition',
                 content_disposition('Brilliant Four Sales Report: Actual Vs Target' + str(wizard.end_date) + '.xlsx'))
            ]
        )

        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_week_style = workbook.add_format(
            {'font_name': 'Calibre', 'font_size': 14, 'bold': True, 'align': 'left', 'num_format': 'd mmm yyyy'})
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

        # layout for Weekly sheet
        week_end_month = wizard.end_date.strftime("%B")
        sheet2 = workbook.add_worksheet('MUTI ' + week_end_month)
        # set the orientation to landscape
        sheet2.set_landscape()
        # set up the paper size, 9 means A4
        sheet2.set_paper(9)
        # set up the margin in inch
        sheet2.set_margins(0.5, 0.5, 0.5, 0.5)

        # set up the column width
        sheet2.set_column('A:B', 20)
        sheet2.set_column('C:D', 17)
        sheet2.set_column('E:E', 13)
        sheet2.set_column('F:G', 17)
        sheet2.set_column('H:H', 13)
        sheet2.set_column('I:J', 17)
        sheet2.set_column('K:K', 13)
        sheet2.set_column('L:M', 17)
        sheet2.set_column('N:N', 13)
        sheet2.set_column('O:P', 17)
        sheet2.set_column('Q:Q', 13)
        sheet2.set_column('R:S', 17)
        sheet2.set_column('T:T', 13)
        sheet2.set_column('U:V', 17)
        sheet2.set_column('W:AB', 17)
        sheet2.merge_range('A1:E1', 'BRILLIANT FOUR HOLDINGS CORPORATION ', title_week_style)
        sheet2.merge_range('A2:E2', 'WEEKLY GM REPORTING TEMPLATE', title_week_style)
        year_str = ' MUTI ' + str(wizard.end_date.year)
        # Merge the range with the year string
        sheet2.merge_range('A3:E3', year_str, title_week_style)

        row2 = 3
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
        row2 = 4
        sheet2.write(row2, col, "Date", header_style)

        current_date = wizard.end_date
        current_date_str = current_date.strftime('%Y-%m-%d')
        sheet2.write(row2, col + 1, current_date_str, header_style)
        row2 += 1
        sheet2.merge_range(row2, col, row2 + 1, col, "KPI", header_style)

        col += 1
        sheet2.merge_range(row2, col, row2 + 1, col, "Remark", header_style)
        cntr = 1
        col += 1
        weekly_results = {}
        weekly = {}
        for week_number, week in enumerate(mth, start=1):
            wk = []
            for day in week:
                if day != 0:
                    dte = '%s-%s-%s' % (target_year, str(target_month).zfill(2), str(day).zfill(2))
                    current_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
                    wk.append(str(current_date))

            weekly_results[tuple(wk)] = wk
            weekly[week_number] = wk

            dte = '%s-%s-%s' % (target_year, target_month, min(wk)[8:10])
            start_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
            dte = '%s-%s-%s' % (target_year, target_month, max(wk)[8:10])
            end_date = datetime.datetime.strptime(dte, '%Y-%m-%d')

            ###-- sales --###
            results2 = self.get_sales_data_muti(wizard, start_date, end_date)
            for res in results2:
                week_grp = '%s - %s' % (cntr, res[0])

                if week_grp not in weekly_results:
                    weekly_results[week_grp] = (res[1], res[2])


            cntr += 1


            week_start_formatted = start_date.strftime("%B %d")
            week_end_formatted = end_date.strftime("%B %d")

            row2 = 4
            sheet2.merge_range(row2, col, row2, col + 1, f'Week {week_number}',
                               header_style)  # Merge cells for week number
            sheet2.write(row2, col + 2, "", header_style)

            row2+=1

            sheet2.merge_range(row2, col, row2, col + 1, f'{week_start_formatted}-{week_end_formatted}',
                               header_style)  # Merge cells for date range
            sheet2.write(row2, col+2, "PERF", header_style)  # Write "PERF" in the next column

            sheet2.write(row2 + 1, col, "Sales", header_style)
            sheet2.write(row2 + 1, col + 1, "Target", header_style)
            sheet2.write(row2 + 1, col + 2, "%", header_style)

            col += 3
        week_end_month = end_date.strftime("%B")
        row2 = 4
        sheet2.merge_range(row2, col, row2, col + 1, 'MONTH OF DATE', header_style)
        sheet2.write(row2, col + 2, "", header_style)
        sheet2.write(row2, col + 3, "", header_style)
        sheet2.write(row2, col + 4, "", header_style)
        sheet2.write(row2, col + 5, "", header_style)
        sheet2.write(row2, col + 6, "", header_style)
        sheet2.merge_range(row2, col + 7, row2, col +8, 'REST OF YEAR', header_style)
        sheet2.write(row2, col + 9, "", header_style)

        row2+=1
        sheet2.merge_range(row2, col,row2, col + 1 , week_end_month, header_style)
        sheet2.write(row2, col + 2, "PERF", header_style)
        sheet2.write(row2, col + 3, "YTD Actual", header_style)
        sheet2.write(row2, col + 4, "YTD Budget", header_style)
        sheet2.merge_range(row2, col + 5, row2, col + 6, 'LAST YEAR()', header_style)
        sheet2.write(row2, col + 7, "INDICATED AT", header_style)
        sheet2.write(row2, col + 8, "ANNUAL BUDGET", header_style)
        sheet2.write(row2, col + 9, "% Age of", header_style)

        sheet2.write(row2 + 1, col, "Sales", header_style)
        sheet2.write(row2 + 1, col+1, "Target", header_style)
        sheet2.write(row2 + 1, col + 2, "%", header_style)
        sheet2.write(row2 + 1, col + 3, "", header_style)
        sheet2.write(row2 + 1, col + 4, "", header_style)
        sheet2.write(row2 + 1, col + 5, "Actual", header_style)
        sheet2.write(row2 + 1, col + 6, "Budget", header_style)
        sheet2.write(row2 + 1, col + 7, "", header_style)
        sheet2.write(row2 + 1, col + 8, "", header_style)
        sheet2.write(row2 + 1, col + 9, "Accomplishment", header_style)




        col += 2


        #### ---- Quantity ---- ####
        row2 += 2
        col = 0
        sheet2.write(row2, col, 'Sales in Unit', text_style)
        col += 1


        end_date = wizard.end_date
        month_start = end_date.replace(day=1)
        next_month = month_start.replace(month=month_start.month % 12 + 1, day=1)

        # Convert dates to strings if necessary (depends on how the ORM handles date comparison)
        month_start_str = month_start.strftime('%Y-%m-%d')
        next_month_str = next_month.strftime('%Y-%m-%d')

        results4 = self.get_sales_month_muti(wizard, end_date)
        for res in results4:
            per_category = res[0]
            sales_this_month_qty = res[1]
            target_this_month_qty = res[3]
            sales_this_ytd_qty = res[5]
            target_this_ytd_qty = res[7]
            sales_last_ytd_qty = res[9]
            target_last_ytd_qty = res[11]
            target_annual_qty = res[13]


            col = 0
            sheet2.write(row2, col + 1, per_category , text_style)
            col += 1

            remaining_target = target_this_month_qty


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


                week_grp = '%s - %s' % (cntr, per_category)

                sales_for_the_week = 0
                if week_grp in weekly_results:
                    if wizard.unit_of_measure == 'quantity':
                        sales_for_the_week = int(weekly_results[week_grp][0])
                    else:
                        sales_for_the_week = int(weekly_results[week_grp][0])



                # get the operation days gamit tong weekend kag holiday
                dte = '%s-%s-%s' % (target_year, target_month, min(d for d in week if d != 0))
                start_week_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
                dte = '%s-%s-%s' % (target_year, target_month, max(d for d in week if d != 0))
                end_week_date = datetime.datetime.strptime(dte, '%Y-%m-%d')

                weekend_holidays = self.get_weekends(start_week_date, end_week_date, holidays)
                operation_days_for_the_week = len([d for d in week if d != 0]) - weekend_holidays

                if target_this_month_qty is None:
                    target_this_month_qty = 0

                if operation_days_for_the_month is None or operation_days_for_the_month == 0:
                    operation_days_for_the_month = 1  # Avoid division by zero, default to 1 if None or zero

                if operation_days_for_the_week is None:
                    operation_days_for_the_week = 0

                if cntr == len(mth):
                    target_for_the_week = remaining_target

                    target_fml = '=%s' % remaining_target
                else:

                    target_for_the_week = round(
                        (target_this_month_qty / operation_days_for_the_month) * operation_days_for_the_week,
                        0)  # print(target_for_the_week)
                    target_fml = '=round((%s / %s) * %s,0)' % (
                        target_this_month_qty, operation_days_for_the_month, operation_days_for_the_week)

                    if remaining_target is not None:
                        remaining_target -= target_for_the_week

                sheet2.write(row2, col + 1, sales_for_the_week,
                             number_style if wizard.unit_of_measure == 'quantity' else number_style)

                sheet2.write(row2, col + 2, target_for_the_week,
                             number_style if wizard.unit_of_measure == 'quantity' else number_style)

                perf_value_formula = '=(%s/%s)' % (sales_for_the_week, target_for_the_week)
                sheet2.write(row2, col + 3, perf_value_formula, percent_format)

                col += 3
                cntr += 1

                sheet2.write(row2, col + 1, sales_this_month_qty, number_style)
                sheet2.write(row2, col + 2, target_this_month_qty, number_style)

                total_qty_formula = '=(%s/%s)' % (sales_this_month_qty, target_this_month_qty)
                sheet2.write(row2, col + 3, total_qty_formula, percent_format)

                sheet2.write(row2, col + 4, sales_this_ytd_qty, number_style)
                sheet2.write(row2, col + 5, target_this_ytd_qty, number_style)
                sheet2.write(row2, col + 6, sales_last_ytd_qty, number_style)
                sheet2.write(row2, col + 7, target_last_ytd_qty, number_style)

                indicated_at = (target_annual_qty - target_this_ytd_qty) + sales_this_ytd_qty

                # Write the result to the Excel sheet in a separate cell (if needed)
                sheet2.write(row2, col + 8, indicated_at, number_style)

                sheet2.write(row2, col + 9, target_annual_qty, number_style)
                age_of_accom = '=(%s/%s)' % (indicated_at, target_annual_qty)

                sheet2.write(row2, col + 10, age_of_accom, percent_format)



            row2 += 1
            col = 0
            col += 3

        #####  ---  VALUE --- ####
        row2 += 1
        col = 0
        sheet2.write(row2, col, 'Sales in Amount', text_style)
        col += 2

        end_date = wizard.end_date
        month_start = end_date.replace(day=1)
        next_month = month_start.replace(month=month_start.month % 12 + 1, day=1)

        # Convert dates to strings if necessary (depends on how the ORM handles date comparison)
        month_start_str = month_start.strftime('%Y-%m-%d')
        next_month_str = next_month.strftime('%Y-%m-%d')

        results4 = self.get_sales_month_muti(wizard, end_date)
        for res in results4:
            per_category = res[0]
            sales_this_month_value = res[2]
            target_this_month_value = res[4]
            sales_this_ytd_value = res[6]
            target_this_ytd_value = res[8]
            sales_last_ytd_value = res[10]
            target_last_ytd_value = res[12]
            target_annual_value = res[14]

            col = 0
            sheet2.write(row2, col + 1, per_category, text_style)
            col += 1

            remaining_target = target_this_month_value


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

                week_grp = '%s - %s' % (cntr, per_category)
                sales_for_the_week = 0
                if week_grp in weekly_results:
                    if wizard.unit_of_measure == 'value':
                        sales_for_the_week = int(weekly_results[week_grp][1])
                    else:
                        sales_for_the_week = int(weekly_results[week_grp][1])

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

                    target_for_the_week = (
                                                      target_this_month_value / operation_days_for_the_month) * operation_days_for_the_week  # print(target_for_the_week)
                    target_fml = '=(%s / %s) * %s' % (
                        target_this_month_value, operation_days_for_the_month, operation_days_for_the_week)

                    remaining_target -= target_for_the_week

                if wizard.unit_of_measure:
                    wizard.unit_of_measure = 'value'
                elif wizard.unit_of_measure == 'quantity':
                    wizard.unit_of_measure = 'value'
                else:
                    wizard.unit_of_measure = wizard.unit_of_measure

                sheet2.write(row2, col + 1, sales_for_the_week,
                             value_style if wizard.unit_of_measure == 'value' else value_style)
                sheet2.write(row2, col + 2, target_for_the_week,
                             value_style if wizard.unit_of_measure == 'value' else value_style)
                perf_value_formula = '=(%s/%s)' % (sales_for_the_week, target_for_the_week)
                sheet2.write(row2, col + 3, perf_value_formula, percent_format)


                col += 3
                cntr += 1

                sheet2.write(row2, col + 1, sales_this_month_value, number_style)
                sheet2.write(row2, col + 2, target_this_month_value, number_style)

                total_value_formula = '=(%s/%s)' % (sales_this_month_value, target_this_month_value)
                sheet2.write(row2, col + 3, total_value_formula, percent_format)

                sheet2.write(row2, col + 4, sales_this_ytd_value, number_style)
                sheet2.write(row2, col + 5, target_this_ytd_value, number_style)
                sheet2.write(row2, col + 6, sales_last_ytd_value, number_style)
                sheet2.write(row2, col + 7, target_last_ytd_value, number_style)

                indicated_at = (target_annual_value - target_this_ytd_value) + sales_this_ytd_value

                # Write the result to the Excel sheet in a separate cell (if needed)
                sheet2.write(row2, col + 8, indicated_at, number_style)

                sheet2.write(row2, col + 9, target_annual_value, number_style)
                age_of_accom = '=(%s/%s)' % (indicated_at, target_annual_value)

                sheet2.write(row2, col + 10, age_of_accom, percent_format)

            row2 += 1
            col = 0
            col += 1

        # layout for Weekly sheet
        week_end_month = wizard.end_date.strftime("%B")
        sheet3 = workbook.add_worksheet('HONDA ' + week_end_month)
        # set the orientation to landscape
        sheet3.set_landscape()
        # set up the paper size, 9 means A4
        sheet3.set_paper(9)
        # set up the margin in inch
        sheet3.set_margins(0.5, 0.5, 0.5, 0.5)

        # set up the column width
        sheet3.set_column('A:B', 20)
        sheet3.set_column('C:D', 17)
        sheet3.set_column('E:E', 13)
        sheet3.set_column('F:G', 17)
        sheet3.set_column('H:H', 13)
        sheet3.set_column('I:J', 17)
        sheet3.set_column('K:K', 13)
        sheet3.set_column('L:M', 17)
        sheet3.set_column('N:N', 13)
        sheet3.set_column('O:P', 17)
        sheet3.set_column('Q:Q', 13)
        sheet3.set_column('R:S', 17)
        sheet3.set_column('T:T', 13)
        sheet3.set_column('U:V', 17)
        sheet3.set_column('W:AB', 17)
        sheet3.merge_range('A1:E1', 'BRILLIANT FOUR HOLDINGS CORPORATION ', title_week_style)
        sheet3.merge_range('A2:E2', 'WEEKLY GM REPORTING TEMPLATE', title_week_style)
        year_str = ' HONDA ' + str(wizard.end_date.year)
        # Merge the range with the year string
        sheet3.merge_range('A3:E3', year_str, title_week_style)

        row4 = 3
        row_start3 = row4

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
        row4 = 4
        sheet3.write(row4, col, "Date", header_style)

        current_date = wizard.end_date
        current_date_str = current_date.strftime('%Y-%m-%d')
        sheet3.write(row4, col + 1, current_date_str, header_style)
        row4 += 1
        sheet3.merge_range(row4, col, row4 + 1, col , "KPI", header_style)

        col += 1
        sheet3.merge_range(row4, col, row4 + 1, col, "Remark", header_style)
        cntr = 1
        col += 1
        weekly_results = {}
        weekly = {}
        for week_number, week in enumerate(mth, start=1):
            wk = []
            for day in week:
                if day != 0:
                    dte = '%s-%s-%s' % (target_year, str(target_month).zfill(2), str(day).zfill(2))
                    current_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
                    wk.append(str(current_date))

            weekly_results[tuple(wk)] = wk
            weekly[week_number] = wk

            dte = '%s-%s-%s' % (target_year, target_month, min(wk)[8:10])
            start_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
            dte = '%s-%s-%s' % (target_year, target_month, max(wk)[8:10])
            end_date = datetime.datetime.strptime(dte, '%Y-%m-%d')

            ###-- sales --###
            results7 = self.get_sales_data_honda(wizard, start_date, end_date)
            for res in results7:
                week_grp = '%s - %s' % (cntr, res[0])

                if week_grp not in weekly_results:
                    weekly_results[week_grp] = (res[1], res[2])

            cntr += 1

            week_start_formatted = start_date.strftime("%B %d")
            week_end_formatted = end_date.strftime("%B %d")

            row4 = 4
            sheet3.merge_range(row4, col, row4, col + 1, f'Week {week_number}',
                               header_style)  # Merge cells for week number
            sheet3.write(row4, col + 2, "", header_style)

            row4 += 1

            sheet3.merge_range(row4, col, row4, col + 1, f'{week_start_formatted}-{week_end_formatted}',
                               header_style)  # Merge cells for date range
            sheet3.write(row4, col + 2, "PERF", header_style)  # Write "PERF" in the next column

            sheet3.write(row4 + 1, col, "Sales", header_style)
            sheet3.write(row4 + 1, col + 1, "Target", header_style)
            sheet3.write(row4 + 1, col + 2, "%", header_style)

            col += 3
        week_end_month = end_date.strftime("%B")
        row4 = 4
        sheet3.merge_range(row4, col, row4, col + 1, 'MONTH OF DATE', header_style)
        sheet3.write(row4, col + 2, "", header_style)
        sheet3.write(row4, col + 3, "", header_style)
        sheet3.write(row4, col + 4, "", header_style)
        sheet3.write(row4, col + 5, "", header_style)
        sheet3.write(row4, col + 6, "", header_style)
        sheet3.merge_range(row4, col + 7, row4, col + 8, 'REST OF YEAR', header_style)
        sheet3.write(row4, col + 9, "", header_style)

        row4 += 1
        sheet3.merge_range(row4, col, row4, col + 1, week_end_month, header_style)
        sheet3.write(row4, col + 2, "PERF", header_style)
        sheet3.write(row4, col + 3, "YTD Actual", header_style)
        sheet3.write(row4, col + 4, "YTD Budget", header_style)
        sheet3.merge_range(row4, col + 5, row4, col + 6, 'LAST YEAR()', header_style)
        sheet3.write(row4, col + 7, "INDICATED AT", header_style)
        sheet3.write(row4, col + 8, "ANNUAL BUDGET", header_style)
        sheet3.write(row4, col + 9, "% Age of", header_style)

        sheet3.write(row4 + 1, col, "Sales", header_style)
        sheet3.write(row4 + 1, col + 1, "Target", header_style)
        sheet3.write(row4 + 1, col + 2, "%", header_style)
        sheet3.write(row4 + 1, col + 3, "", header_style)
        sheet3.write(row4 + 1, col + 4, "", header_style)
        sheet3.write(row4 + 1, col + 5, "Actual", header_style)
        sheet3.write(row4 + 1, col + 6, "Budget", header_style)
        sheet3.write(row4 + 1, col + 7, "", header_style)
        sheet3.write(row4 + 1, col + 8, "", header_style)
        sheet3.write(row4 + 1, col + 9, "Accomplishment", header_style)

        col += 2

        #### ---- Quantity ---- ####
        row4 += 2
        col = 0
        sheet3.write(row4, col, 'Sales in Unit', text_style)
        col += 1

        end_date = wizard.end_date
        month_start = end_date.replace(day=1)
        next_month = month_start.replace(month=month_start.month % 12 + 1, day=1)

        # Convert dates to strings if necessary (depends on how the ORM handles date comparison)
        month_start_str = month_start.strftime('%Y-%m-%d')
        next_month_str = next_month.strftime('%Y-%m-%d')

        results6 = self.get_sales_month_honda(wizard, end_date)
        for res in results6:
            per_category = res[0]
            sales_this_month_qty = res[1]
            target_this_month_qty = res[3]
            sales_this_ytd_qty = res[5]
            target_this_ytd_qty = res[7]
            sales_last_ytd_qty = res[9]
            target_last_ytd_qty = res[11]
            target_annual_qty = res[13]

            col = 0
            sheet3.write(row4, col + 1, per_category, text_style)
            col += 1

            remaining_target = target_this_month_qty

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

                week_grp = '%s - %s' % (cntr, per_category)

                sales_for_the_week = 0
                if week_grp in weekly_results:
                    if wizard.unit_of_measure == 'quantity':
                        sales_for_the_week = int(weekly_results[week_grp][0])
                    else:
                        sales_for_the_week = int(weekly_results[week_grp][0])

                # get the operation days gamit tong weekend kag holiday
                dte = '%s-%s-%s' % (target_year, target_month, min(d for d in week if d != 0))
                start_week_date = datetime.datetime.strptime(dte, '%Y-%m-%d')
                dte = '%s-%s-%s' % (target_year, target_month, max(d for d in week if d != 0))
                end_week_date = datetime.datetime.strptime(dte, '%Y-%m-%d')

                weekend_holidays = self.get_weekends(start_week_date, end_week_date, holidays)
                operation_days_for_the_week = len([d for d in week if d != 0]) - weekend_holidays

                if target_this_month_qty is None:
                    target_this_month_qty = 0

                if operation_days_for_the_month is None or operation_days_for_the_month == 0:
                    operation_days_for_the_month = 1  # Avoid division by zero, default to 1 if None or zero

                if operation_days_for_the_week is None:
                    operation_days_for_the_week = 0

                if cntr == len(mth):
                    target_for_the_week = remaining_target

                    target_fml = '=%s' % remaining_target
                else:

                    target_for_the_week = round(
                        (target_this_month_qty / operation_days_for_the_month) * operation_days_for_the_week,
                        0)  # print(target_for_the_week)
                    target_fml = '=round((%s / %s) * %s,0)' % (
                        target_this_month_qty, operation_days_for_the_month, operation_days_for_the_week)

                    if remaining_target is not None:
                        remaining_target -= target_for_the_week

                sheet3.write(row4, col + 1, sales_for_the_week,
                             number_style if wizard.unit_of_measure == 'quantity' else number_style)

                sheet3.write(row4, col + 2, target_for_the_week,
                             number_style if wizard.unit_of_measure == 'quantity' else number_style)

                perf_value_formula = '=(%s/%s)' % (sales_for_the_week, target_for_the_week)
                sheet3.write(row4, col + 3, perf_value_formula, percent_format)

                col += 3
                cntr += 1

                sheet3.write(row4, col + 1, sales_this_month_qty, number_style)
                sheet3.write(row4, col + 2, target_this_month_qty, number_style)

                total_qty_formula = '=(%s/%s)' % (sales_this_month_qty, target_this_month_qty)
                sheet3.write(row4, col + 3, total_qty_formula, percent_format)

                sheet3.write(row4, col + 4, sales_this_ytd_qty, number_style)
                sheet3.write(row4, col + 5, target_this_ytd_qty, number_style)
                sheet3.write(row4, col + 6, sales_last_ytd_qty, number_style)
                sheet3.write(row4, col + 7, target_last_ytd_qty, number_style)

                indicated_at = (target_annual_qty - target_this_ytd_qty) + sales_this_ytd_qty

                # Write the result to the Excel sheet in a separate cell (if needed)
                sheet3.write(row4, col + 8, indicated_at, number_style)

                sheet3.write(row4, col + 9, target_annual_qty, number_style)
                age_of_accom = '=(%s/%s)' % (indicated_at, target_annual_qty)

                sheet3.write(row4, col + 10, age_of_accom, percent_format)

            row4 += 1
            col = 0
            col += 3

        #####  ---  VALUE --- ####
        row4 += 1
        col = 0
        sheet3.write(row4, col, 'Sales in Amount', text_style)
        col += 2

        end_date = wizard.end_date
        month_start = end_date.replace(day=1)
        next_month = month_start.replace(month=month_start.month % 12 + 1, day=1)

        # Convert dates to strings if necessary (depends on how the ORM handles date comparison)
        month_start_str = month_start.strftime('%Y-%m-%d')
        next_month_str = next_month.strftime('%Y-%m-%d')

        results6 = self.get_sales_month_honda(wizard, end_date)
        for res in results6:
            per_category = res[0]
            sales_this_month_value = res[2]
            target_this_month_value = res[4]
            sales_this_ytd_value = res[6]
            target_this_ytd_value = res[8]
            sales_last_ytd_value = res[10]
            target_last_ytd_value = res[12]
            target_annual_value = res[14]

            col = 0
            sheet3.write(row4, col + 1, per_category, text_style)
            col += 1

            remaining_target = target_this_month_value

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

                week_grp = '%s - %s' % (cntr, per_category)
                sales_for_the_week = 0
                if week_grp in weekly_results:
                    if wizard.unit_of_measure == 'value':
                        sales_for_the_week = int(weekly_results[week_grp][1])
                    else:
                        sales_for_the_week = int(weekly_results[week_grp][1])

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

                    target_for_the_week = (
                                                  target_this_month_value / operation_days_for_the_month) * operation_days_for_the_week  # print(target_for_the_week)
                    target_fml = '=(%s / %s) * %s' % (
                        target_this_month_value, operation_days_for_the_month, operation_days_for_the_week)

                    remaining_target -= target_for_the_week

                if wizard.unit_of_measure:
                    wizard.unit_of_measure = 'value'
                elif wizard.unit_of_measure == 'quantity':
                    wizard.unit_of_measure = 'value'
                else:
                    wizard.unit_of_measure = wizard.unit_of_measure

                sheet3.write(row4, col + 1, sales_for_the_week,
                             value_style if wizard.unit_of_measure == 'value' else value_style)
                sheet3.write(row4, col + 2, target_for_the_week,
                             value_style if wizard.unit_of_measure == 'value' else value_style)
                perf_value_formula = '=(%s/%s)' % (sales_for_the_week, target_for_the_week)
                sheet3.write(row4, col + 3, perf_value_formula, percent_format)

                col += 3
                cntr += 1

                sheet3.write(row4, col + 1, sales_this_month_value, number_style)
                sheet3.write(row4, col + 2, target_this_month_value, number_style)

                total_value_formula = '=(%s/%s)' % (sales_this_month_value, target_this_month_value)
                sheet3.write(row4, col + 3, total_value_formula, percent_format)

                sheet3.write(row4, col + 4, sales_this_ytd_value, number_style)
                sheet3.write(row4, col + 5, target_this_ytd_value, number_style)
                sheet3.write(row4, col + 6, sales_last_ytd_value, number_style)
                sheet3.write(row4, col + 7, target_last_ytd_value, number_style)

                indicated_at = (target_annual_value - target_this_ytd_value) + sales_this_ytd_value

                # Write the result to the Excel sheet in a separate cell (if needed)
                sheet3.write(row4, col + 8, indicated_at, number_style)

                sheet3.write(row4, col + 9, target_annual_value, number_style)
                age_of_accom = '=(%s/%s)' % (indicated_at, target_annual_value)

                sheet3.write(row4, col + 10, age_of_accom, percent_format)

            row4 += 1
            col = 0
            col += 1

        sheet4 = workbook.add_worksheet('QTD - YTD')
        # set the orientation to landscape
        sheet4.set_landscape()
        # set up the paper size, 9 means A4
        sheet4.set_paper(9)
        # set up the margin in inch
        sheet4.set_margins(0.5, 0.5, 0.5, 0.5)

        # set up the column width
        sheet4.set_column('A:B', 25)
        sheet4.set_column('C:Q', 15)

        sheet4.merge_range('A1:E1', 'BRILLIANT FOUR HOLDINGS CORPORATION ', title_style)
        sheet4.merge_range('A2:E2', 'WEEKLY GM REPORTING TEMPLATE', title_style)
        sheet4.merge_range('A3:E3', 'MUTI 2023', title_style)
        sheet4.merge_range('A4:J4', 'QUARTER SUMMARY AND YTD PERFORMANCE', header_style)

        col = 0
        row3 = 4
        sheet4.merge_range(row3, col, row3 + 1, col, "KPI", header_style)
        sheet4.write(row3 + 2, col, "DATE", header_style)

        col += 1

        sheet4.merge_range(row3, col, row3 + 1, col, "Remark", header_style)
        sheet4.write(row3 + 2, col, "", header_style)


        col += 1

        sheet4.merge_range(row3, col, row3, col + 1, "Q1", header_style)
        sheet4.merge_range(row3 + 1, col, row3 + 1, col + 1, "JAN - MARCH", header_style)
        sheet4.write(row3 + 2, col, "ACTUAL", header_style)
        sheet4.write(row3 + 2, col + 1, "TGT", header_style)

        col += 1

        sheet4.write(row3, col + 1, "SQLY", header_style)
        sheet4.write(row3 + 1, col + 1 , "2023", header_style)
        sheet4.write(row3 + 2, col + 1, "ACTUAL", header_style)

        col += 1

        sheet4.write(row3, col + 1, "GW", header_style)
        sheet4.write(row3 + 1, col + 1, "%", header_style)
        sheet4.write(row3 + 2, col + 1, " ", header_style)

        col += 2

        sheet4.merge_range(row3, col, row3, col + 1, "YTD", header_style)
        sheet4.merge_range(row3 + 1, col, row3 + 1, col + 1, "2024", header_style)
        sheet4.write(row3 + 2, col, "ACTUAL", header_style)
        sheet4.write(row3 + 2, col + 1, "TGT", header_style)

        col += 1

        sheet4.write(row3, col + 1, "PERF", header_style)
        sheet4.write(row3 + 1, col + 1, "%", header_style)
        sheet4.write(row3 + 2, col + 1, " ", header_style)

        col += 1

        sheet4.write(row3, col + 1, "BALANCE TO SELL", header_style)
        sheet4.write(row3 + 1, col + 1, "(TGT - ACTUAL)", header_style)
        sheet4.write(row3 + 2, col + 1, " ", header_style)

        row3 += 3
        col = 0
        sheet4.write(row3, col, 'Sales in Unit', text_style)
        col += 2

        end_date = wizard.end_date

        results5 = self.get_sales_target_data(wizard, end_date)
        for res in results5:
            product_category = res[0]
            actual_q1_qty = res[3]
            target_q1_qty = res[9]
            actual_last_ytd_qty = res[1]
            actual_this_ytd_qty = res[5]
            target_this_ytd_qty = res[11]

            perf_this_ytd_qty = '=(%s/%s)' % (actual_this_ytd_qty, target_this_ytd_qty)
            bal_this_ytd_qty = '=(%s-%s)' % (actual_this_ytd_qty, target_this_ytd_qty)

            col = 0
            sheet4.write(row3, col + 1, product_category, text_style)
            sheet4.write(row3, col + 2, actual_q1_qty, number_style)
            sheet4.write(row3, col + 3, target_q1_qty, number_style)
            sheet4.write(row3, col + 4, actual_last_ytd_qty, number_style)
            sheet4.write(row3, col + 5, '', percent_format)
            sheet4.write(row3, col + 6, actual_this_ytd_qty, number_style)
            sheet4.write(row3, col + 7, target_this_ytd_qty, number_style)
            sheet4.write(row3, col + 8, perf_this_ytd_qty, percent_format)
            sheet4.write(row3, col + 9, bal_this_ytd_qty, number_style)
            row3 += 1
            col += 1
        row3 += 1
        col = 0
        sheet4.write(row3, col, 'Sales in Amount', text_style)
        col += 2

        end_date = wizard.end_date
        results5 = self.get_sales_target_data(wizard, end_date)
        for res in results5:
            product_category = res[0]
            actual_q1_value = res[4]
            target_q1_value = res[10]
            actual_last_ytd_value = res[2]
            actual_this_ytd_value = res[6]
            target_this_ytd_value = res[12]

            perf_this_ytd_value = '=(%s/%s)' % (actual_this_ytd_value, target_this_ytd_value)
            bal_this_ytd_value = '=(%s-%s)' % (actual_this_ytd_value, target_this_ytd_value)

            col = 0
            sheet4.write(row3, col + 1, product_category, text_style)
            sheet4.write(row3, col + 2, actual_q1_value, number_style)
            sheet4.write(row3, col + 3, target_q1_value, number_style)
            sheet4.write(row3, col + 4, actual_last_ytd_value, number_style)
            sheet4.write(row3, col + 5, '', percent_format)
            sheet4.write(row3, col + 6, actual_this_ytd_value, number_style)
            sheet4.write(row3, col + 7, target_this_ytd_value, number_style)
            sheet4.write(row3, col + 8, perf_this_ytd_value, percent_format)
            sheet4.write(row3, col + 9, bal_this_ytd_value, number_style)
            row3 += 1
            col += 1






        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response

    def get_sales_data_muti(self, wizard, start_date, end_date):

        where_cond = ''

        query2 = f"""WITH sales AS (
                    SELECT
                        product_category,
                        SUM(qty) as actual_this_week_qty,
                        SUM(amount) as actual_this_week_value
                    FROM
                        sales_summary
                    WHERE
                        date(date) between '{start_date}' and '{end_date}' AND
                        (company = 'MUTI' OR vendor_name = 'MUTI')
                    GROUP BY
                        product_category
                )

                SELECT  
                    a.product_category,
                    a.actual_this_week_qty,
                    a.actual_this_week_value
                FROM
                    sales a
                """

        wizard.env.cr.execute(query2)
        results2 = wizard.env.cr.fetchall()
        return results2

    def get_sales_data_honda(self, wizard, start_date, end_date):

        where_cond = ''

        query7 = f"""WITH sales AS (
                    SELECT
                        product_category,
                        SUM(qty) as actual_this_week_qty,
                        SUM(amount) as actual_this_week_value
                    FROM
                        sales_summary
                    WHERE
                        date(date) between '{start_date}' and '{end_date}' AND
                        (company = 'HSI' OR vendor_name = 'HSI')
                    GROUP BY
                        product_category
                )

                SELECT  
                    a.product_category,
                    a.actual_this_week_qty,
                    a.actual_this_week_value
                FROM
                    sales a
                """

        wizard.env.cr.execute(query7)
        results7 = wizard.env.cr.fetchall()
        return results7

    def get_sales_month_muti(self, wizard,end_date):

        query4 = f"""
                       WITH all_categories AS (
                    SELECT DISTINCT product_category FROM sales_summary
                    UNION
                    SELECT DISTINCT target_category AS product_category FROM target_cpmrp_config
                ),
                sales AS (
                    SELECT
                        product_category,
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((DATE '{end_date}' - interval '1 year'), 'YYYY')
                            THEN qty 
                        END) AS actual_last_ytd_qty,
                     
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY') = TO_CHAR(DATE '{end_date}', 'YYYY')
                            AND date <= DATE '{end_date}'
                            THEN qty 
                        END) AS actual_this_ytd_qty,
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((DATE '{end_date}' - interval '1 year'), 'YYYY')
                            THEN amount 
                        END) AS actual_last_ytd_amount,
                      
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY') = TO_CHAR(DATE '{end_date}', 'YYYY')
                            AND date <= DATE '{end_date}'
                            THEN amount 
                        END) AS actual_this_ytd_amount,
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY-MM') = TO_CHAR(DATE '{end_date}', 'YYYY-MM')
                            THEN qty 
                        END) AS actual_this_month_qty,
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY-MM') = TO_CHAR(DATE '{end_date}', 'YYYY-MM')
                            THEN amount 
                        END) AS actual_this_month_amount
                    FROM
                        sales_summary
                    WHERE
                        date(date) >= DATE_TRUNC('year', DATE '{end_date}')
                        AND date(date) <= DATE '{end_date}' AND (company = 'MUTI' OR vendor_name = 'MUTI')
                    GROUP BY
                        product_category
                ),
                target AS (
                    SELECT
                        target_category AS product_category,
                        SUM(CASE 
                            WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((DATE '{end_date}' - INTERVAL '1 year'), 'YYYY') 
                            THEN CAST(target_quantity AS FLOAT) 
                        END) AS target_last_ytd_qty,
                        SUM(CASE 
                            WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((DATE '{end_date}' - INTERVAL '1 year'), 'YYYY') 
                            THEN CAST(target_value AS FLOAT) 
                        END) AS target_last_ytd_amount,
                        SUM(CASE 
                            WHEN target_date BETWEEN DATE_TRUNC('year', DATE '{end_date}') AND DATE '{end_date}'
                            THEN CAST(target_quantity AS FLOAT) 
                        END) AS target_this_ytd_qty,
                        SUM(CASE 
                            WHEN target_date BETWEEN DATE_TRUNC('year', DATE '{end_date}') AND DATE '{end_date}'
                            THEN CAST(target_value AS FLOAT) 
                        END) AS target_this_ytd_amount,
                        SUM(CASE 
                            WHEN TO_CHAR(target_date, 'YYYY-MM') = TO_CHAR(DATE '{end_date}', 'YYYY-MM')
                            THEN CAST(target_quantity AS FLOAT) 
                        END) AS target_this_month_qty,
                        SUM(CASE 
                            WHEN TO_CHAR(target_date, 'YYYY-MM') = TO_CHAR(DATE '{end_date}', 'YYYY-MM')
                            THEN CAST(target_value AS FLOAT) 
                        END) AS target_this_month_amount,
                        SUM(CASE 
                            WHEN target_date BETWEEN DATE_TRUNC('year', DATE '{end_date}') AND (DATE_TRUNC('year', DATE '{end_date}') + INTERVAL '1 year - 1 day')
                            THEN CAST(target_quantity AS FLOAT)
                        END) AS target_annual_qty,
                        SUM(CASE 
                            WHEN target_date BETWEEN DATE_TRUNC('year', DATE '{end_date}') AND (DATE_TRUNC('year', DATE '{end_date}') + INTERVAL '1 year - 1 day')
                            THEN CAST(target_value AS FLOAT)
                        END) AS target_annual_amount
                    FROM
                        target_cpmrp_config
                    WHERE
                        target_company = 'MUTI'
                    GROUP BY
                        target_category
                )
                SELECT
                    ac.product_category,
                    COALESCE(s.actual_this_month_qty, 0) AS actual_this_month_qty,
                    COALESCE(s.actual_this_month_amount, 0) AS actual_this_month_amount,
                    COALESCE(t.target_this_month_qty, 0) AS target_this_month_qty,
                    COALESCE(t.target_this_month_amount, 0) AS target_this_month_amount,
                    COALESCE(s.actual_this_ytd_qty, 0) AS actual_this_ytd_qty,
                    COALESCE(s.actual_this_ytd_amount, 0) AS actual_this_ytd_amount,
                    COALESCE(t.target_this_ytd_qty, 0) AS target_this_ytd_qty,
                    COALESCE(t.target_this_ytd_amount, 0) AS target_this_ytd_amount,
                    COALESCE(s.actual_last_ytd_qty, 0) AS actual_last_ytd_qty,
                    COALESCE(s.actual_last_ytd_amount, 0) AS actual_last_ytd_amount,
                    COALESCE(t.target_last_ytd_qty, 0) AS target_last_ytd_qty,
                    COALESCE(t.target_last_ytd_amount, 0) AS target_last_ytd_amount,
                    COALESCE(t.target_annual_qty, 0) AS target_annual_qty,
                    COALESCE(t.target_annual_amount, 0) AS target_annual_amount
                    
                FROM
                    all_categories ac
                LEFT JOIN
                    sales s ON ac.product_category = s.product_category
                LEFT JOIN
                    target t ON ac.product_category = t.product_category;
        """
        wizard.env.cr.execute(query4)
        print(query4)
        results4 = wizard.env.cr.fetchall()
        return results4

    def get_sales_month_honda(self, wizard, end_date):

        query6 = f"""
                       WITH all_categories AS (
                    SELECT DISTINCT product_category FROM sales_summary
                    UNION
                    SELECT DISTINCT target_category AS product_category FROM target_cpmrp_config
                ),
                sales AS (
                    SELECT
                        product_category,
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((DATE '{end_date}' - interval '1 year'), 'YYYY')
                            THEN qty 
                        END) AS actual_last_ytd_qty,

                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY') = TO_CHAR(DATE '{end_date}', 'YYYY')
                            AND date <= DATE '{end_date}'
                            THEN qty 
                        END) AS actual_this_ytd_qty,
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((DATE '{end_date}' - interval '1 year'), 'YYYY')
                            THEN amount 
                        END) AS actual_last_ytd_amount,

                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY') = TO_CHAR(DATE '{end_date}', 'YYYY')
                            AND date <= DATE '{end_date}'
                            THEN amount 
                        END) AS actual_this_ytd_amount,
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY-MM') = TO_CHAR(DATE '{end_date}', 'YYYY-MM')
                            THEN qty 
                        END) AS actual_this_month_qty,
                        SUM(CASE 
                            WHEN TO_CHAR(date, 'YYYY-MM') = TO_CHAR(DATE '{end_date}', 'YYYY-MM')
                            THEN amount 
                        END) AS actual_this_month_amount
                    FROM
                        sales_summary
                    WHERE
                        date(date) >= DATE_TRUNC('year', DATE '{end_date}')
                        AND date(date) <= DATE '{end_date}' AND (company = 'HSI' OR vendor_name = 'HSI')
                    GROUP BY
                        product_category
                ),
                target AS (
                    SELECT
                        target_category AS product_category,
                        SUM(CASE 
                            WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((DATE '{end_date}' - INTERVAL '1 year'), 'YYYY') 
                            THEN CAST(target_quantity AS FLOAT) 
                        END) AS target_last_ytd_qty,
                        SUM(CASE 
                            WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((DATE '{end_date}' - INTERVAL '1 year'), 'YYYY') 
                            THEN CAST(target_value AS FLOAT) 
                        END) AS target_last_ytd_amount,
                        SUM(CASE 
                            WHEN target_date BETWEEN DATE_TRUNC('year', DATE '{end_date}') AND DATE '{end_date}'
                            THEN CAST(target_quantity AS FLOAT) 
                        END) AS target_this_ytd_qty,
                        SUM(CASE 
                            WHEN target_date BETWEEN DATE_TRUNC('year', DATE '{end_date}') AND DATE '{end_date}'
                            THEN CAST(target_value AS FLOAT) 
                        END) AS target_this_ytd_amount,
                        SUM(CASE 
                            WHEN TO_CHAR(target_date, 'YYYY-MM') = TO_CHAR(DATE '{end_date}', 'YYYY-MM')
                            THEN CAST(target_quantity AS FLOAT) 
                        END) AS target_this_month_qty,
                        SUM(CASE 
                            WHEN TO_CHAR(target_date, 'YYYY-MM') = TO_CHAR(DATE '{end_date}', 'YYYY-MM')
                            THEN CAST(target_value AS FLOAT) 
                        END) AS target_this_month_amount,
                        SUM(CASE 
                            WHEN target_date BETWEEN DATE_TRUNC('year', DATE '{end_date}') AND (DATE_TRUNC('year', DATE '{end_date}') + INTERVAL '1 year - 1 day')
                            THEN CAST(target_quantity AS FLOAT)
                        END) AS target_annual_qty,
                        SUM(CASE 
                            WHEN target_date BETWEEN DATE_TRUNC('year', DATE '{end_date}') AND (DATE_TRUNC('year', DATE '{end_date}') + INTERVAL '1 year - 1 day')
                            THEN CAST(target_value AS FLOAT)
                        END) AS target_annual_amount
                    FROM
                        target_cpmrp_config
                    WHERE
                        target_company = 'HSI'
                    GROUP BY
                        target_category
                )
                SELECT
                    ac.product_category,
                    COALESCE(s.actual_this_month_qty, 0) AS actual_this_month_qty,
                    COALESCE(s.actual_this_month_amount, 0) AS actual_this_month_amount,
                    COALESCE(t.target_this_month_qty, 0) AS target_this_month_qty,
                    COALESCE(t.target_this_month_amount, 0) AS target_this_month_amount,
                    COALESCE(s.actual_this_ytd_qty, 0) AS actual_this_ytd_qty,
                    COALESCE(s.actual_this_ytd_amount, 0) AS actual_this_ytd_amount,
                    COALESCE(t.target_this_ytd_qty, 0) AS target_this_ytd_qty,
                    COALESCE(t.target_this_ytd_amount, 0) AS target_this_ytd_amount,
                    COALESCE(s.actual_last_ytd_qty, 0) AS actual_last_ytd_qty,
                    COALESCE(s.actual_last_ytd_amount, 0) AS actual_last_ytd_amount,
                    COALESCE(t.target_last_ytd_qty, 0) AS target_last_ytd_qty,
                    COALESCE(t.target_last_ytd_amount, 0) AS target_last_ytd_amount,
                    COALESCE(t.target_annual_qty, 0) AS target_annual_qty,
                    COALESCE(t.target_annual_amount, 0) AS target_annual_amount

                FROM
                    all_categories ac
                LEFT JOIN
                    sales s ON ac.product_category = s.product_category
                LEFT JOIN
                    target t ON ac.product_category = t.product_category;
        """
        wizard.env.cr.execute(query6)
        print(query6)
        results6 = wizard.env.cr.fetchall()
        return results6



    def get_weekends(self, start_date, end_date, holidays=None):
        days = [date.fromordinal(d) for d in
                range(start_date.toordinal(),
                      end_date.toordinal() + 1)]

        weekend_days = [d for d in days if d.weekday() == SUN]
        holidays_days = [d for d in days if d in holidays]

        return len(weekend_days) + len(holidays_days)


    def get_sales_target_data(self, wizard, end_date):

        query5 = f"""WITH all_categories AS (
                SELECT DISTINCT product_category FROM sales_summary
                UNION
                SELECT DISTINCT target_category AS product_category FROM target_cpmrp_config
             ),
            sales AS (
                SELECT
                    product_category,
                   SUM(CASE WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((date('{end_date}') - interval '1 year'), 'YYYY')
                                THEN qty end) as actual_last_ytd_qty,
				   SUM(CASE 
					WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((date '{end_date}'), 'YYYY')
					AND EXTRACT(QUARTER FROM date) = 1
					THEN qty 
				END) AS actual_this_q1_qty,
				SUM(CASE WHEN TO_CHAR(date, 'YYYY') = TO_CHAR(date '{end_date}', 'YYYY')
					AND date <= date '2024-06-06'
					THEN qty 
				END) AS actual_this_ytd_qty,
				SUM(CASE WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((date('{end_date}') - interval '1 year'), 'YYYY')
                                THEN amount end) as actual_last_ytd_amount,
				SUM(CASE 
					WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((date '{end_date}'), 'YYYY')
					AND EXTRACT(QUARTER FROM date) = 1
					THEN amount 
				END) AS actual_this_q1_amount,
				SUM(CASE WHEN TO_CHAR(date, 'YYYY') = TO_CHAR(date '{end_date}', 'YYYY')
					AND date <= date '{end_date}'
					THEN amount 
				END) AS actual_this_ytd_amount
				
                FROM
                    sales_summary
                WHERE
                   date(date) >= date_trunc('year', (date('{end_date}') - interval '1 year'))
                                and date(date) <= '{end_date}'
                GROUP BY
                    product_category
            ),
            target AS (
                SELECT
                    target_category AS product_category,
					SUM(CASE 
                WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((DATE '{end_date}' - INTERVAL '1 year'), 'YYYY') 
                THEN CAST(target_quantity AS FLOAT) 
            END) AS target_last_ytd_qty,
				SUM(CASE 
                WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((DATE '{end_date}' - INTERVAL '1 year'), 'YYYY') 
                THEN CAST(target_value AS FLOAT) 
            END) AS target_last_ytd_amount,
				SUM(CASE 
					WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((date '{end_date}'), 'YYYY')
					AND EXTRACT(QUARTER FROM target_date) = 1
					THEN CAST(target_quantity AS FLOAT)
				END) AS target_this_q1_qty,
				SUM(CASE 
					WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((date '{end_date}'), 'YYYY')
					AND EXTRACT(QUARTER FROM target_date) = 1
					THEN CAST(target_value AS FLOAT)
				END) AS target_this_q1_amount,
				SUM(CASE 
                WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((DATE '{end_date}'), 'YYYY') 
                THEN CAST(target_quantity AS FLOAT) 
            END) AS target_this_ytd_qty,
				SUM(CASE 
                WHEN TO_CHAR(target_date, 'YYYY') = TO_CHAR((DATE '{end_date}'), 'YYYY') 
                THEN CAST(target_value AS FLOAT) 
            END) AS target_this_ytd_amount
                FROM
                    target_cpmrp_config
                WHERE
                    date(target_date) >= date_trunc('year', (date('{end_date}') - interval '1 year'))
                                and date(target_date) <= '{end_date}'
                GROUP BY
                    target_category
            )
            SELECT
                ac.product_category,
                COALESCE(s.actual_last_ytd_qty, 0) AS actual_last_ytd_qty,
				COALESCE(s.actual_last_ytd_amount, 0) AS actual_last_ytd_amount,
                COALESCE(s.actual_this_q1_qty, 0) AS actual_this_q1_qty,
				COALESCE(s.actual_this_q1_amount, 0) AS actual_this_q1_amount,
				COALESCE(s.actual_this_ytd_qty, 0) AS actual_this_ytd_qty,
				COALESCE(s.actual_this_ytd_amount, 0) AS actual_this_ytd_amount,
                COALESCE(t.target_last_ytd_qty, 0) AS target_last_ytd_qty,
				COALESCE(t.target_last_ytd_amount, 0) AS target_last_ytd_amount,
				COALESCE(t.target_this_q1_qty, 0) AS target_this_q1_qty,
				COALESCE(t.target_this_q1_amount, 0) AS target_this_q1_amount,
				COALESCE(t.target_this_ytd_qty, 0) AS target_this_ytd_qty,
				COALESCE(t.target_this_ytd_amount, 0) AS target_this_ytd_amount
				
            FROM
                all_categories ac
            LEFT JOIN
                sales s ON ac.product_category = s.product_category
            LEFT JOIN
                target t ON ac.product_category = t.product_category;
                """

        wizard.env.cr.execute(query5)
        results5 = wizard.env.cr.fetchall()
        print(query5)
        return results5

    def get_weekends(self, start_date, end_date, holidays=None):
        days = [date.fromordinal(d) for d in
                range(start_date.toordinal(),
                      end_date.toordinal() + 1)]

        weekend_days = [d for d in days if d.weekday() == SUN]
        holidays_days = [d for d in days if d in holidays]

        return len(weekend_days) + len(holidays_days)

    def week_of_month(self, start_date):
        first_day = start_date.replace(day=1)
        day_of_month = start_date.day
        adjusted_day_of_week = first_day.weekday()  # 0-based day of week for the first day of the month
        return (day_of_month + adjusted_day_of_week - 1) // 7 + 1
