from odoo import models, fields, api


class MyWizard(models.TransientModel):
    _name = 'sales.wizard'
    _description = 'Sales Wizard'

    criteria = fields.Selection([('area', 'Area'), ('branch', 'Branch'), ('standard_description', 'Product'),
                                 ('product_category', 'Product Group'), ('brand', 'Brand'), ('usage', 'Usage')],
                                string='Group By', required=True, default='brand')
    unit_of_measure = fields.Selection([('quantity', 'Quantity'), ('value', 'Value')],
                                       string='Unit of Measure', required=True, default='value')
    end_date = fields.Date(string='End Date', required=True, default=fields.Datetime.now())
    time_series = fields.Selection([('week', 'Weekly'), ('month', 'Monthly')],
                                   string='Time Series', required=True, default='month')
    brand_ids = fields.Many2many('sales.brand', string='Brand')
    description_ids = fields.Many2many('sales.description', string='Product')
    default_description_ids = fields.Many2many('sales.description', 'brand_product', string="All Products")
    category_ids = fields.Many2many('sales.category', string='Product Group')
    branch_ids = fields.Many2many('sales.branch', string='Branch')
    area_ids = fields.Many2many('sales.area', string='Sales Area')
    default_branch_ids = fields.Many2many('sales.branch', 'area_based_branch', string="All Branches")
    usage_ids = fields.Many2many('sales.usage', string='Usage')
    company_ids = fields.Many2many('sales.company', string='Company')
    type_ids = fields.Many2many('sales.type', string='Sales Type')
    outlet_ids = fields.Many2many('sales.outlet', string='Class Outlet')
    customer_ids = fields.Many2many('sales.customer', string='Customer Type')
    service_ids = fields.Many2many('sales.service', string='Service Type')
    category_sales = fields.Selection([('gross sale', 'Gross Sales'), ('return sales', ' Return Sales'),
                                       ('discount sales', 'Discount Sales'), ('net sales', 'Net Sales')],
                                      string='Sales Category')

    # result1_ids = fields.One2many('sales.list', 'wizard1_id', string='Results')
    result2_ids = fields.One2many('sales.list', 'wizard2_id', string='Results')

    unit = fields.Boolean('Hide Column')

    def get_sales_dashboard_excel_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/sales_dashboard/get_sales_dashboard_excel_report/%s' % (self.id),
            'target': 'new',
        }

    # use area field and company field to fetch specific branches
    @api.onchange('area_ids', 'company_ids')
    def _onchange_area_ids(self):
        # if no area or company is selected
        if not self.area_ids and not self.company_ids:
            self.default_branch_ids = self.env['sales.branch'].search([('id', '!=', 0)])
        else:
            def_branches = self.env['sales.branch']
            # if no company is selected and an area is selected
            if not self.company_ids:
                for area in self.area_ids:
                    def_branches += self.env['sales.branch'].search([('area_name', '=', area.area_name)])
            # if no area is selected and a company is selected
            if not self.area_ids:
                for company in self.company_ids:
                    def_branches += self.env['sales.branch'].search([('company_name', '=', company.company_name)])
            # if an area and a company are both selected
            else:
                for area, company in zip(self.area_ids, self.company_ids):
                    def_branches += self.env['sales.branch'].search([('area_name', '=', area.area_name),
                                                                  ('company_name', '=', company.company_name)])
            # selected branches based on area field and company field
            self.default_branch_ids = def_branches

    # use brand field and category field to fetch specific products
    @api.onchange('brand_ids', 'category_ids')
    def _onchange_brand_ids(self):
        # if no brand or category is selected
        if not self.brand_ids and not self.category_ids:
            self.default_description_ids = self.env['sales.description'].search([('id', '!=', 0)])
        else:
            def_products = self.env['sales.description']
            # if no product category/group is selected and a brand is selected
            if not self.category_ids:
                for brand in self.brand_ids:
                    def_products += self.env['sales.description'].search([('brand', '=', brand.brand_name)])
            # if no product category/group is selected and a brand is selected
            if not self.brand_ids:
                for category in self.category_ids:
                    def_products += self.env['sales.description'].search([('product_category', '=', category.categ_name)])
            # if a brand and a product category/group are both selected
            else:
                for brand, category in zip(self.brand_ids, self.category_ids):
                    def_products += self.env['sales.description'].search([('brand', '=', brand.brand_name),
                                                                     ('product_category', '=', category.categ_name)])
            # selected products based on brand field and product category/group field
            self.default_description_ids = def_products

    # generate wizard tree view
    def generate_tree_view(self):
        group_by = self.criteria
        order_date = self.end_date

        where_cond = ''
        target_cond = ''
        target_group = ''
        grouping = ''
        join_table = ''

        # DB fields of target sales and actual sales
        if group_by == 'area':
            target_group = 't.area'
            grouping = 'area'
        if group_by == 'branch':
            target_group = 't.branch_name'
            grouping = 'area'
        if group_by == 'standard_description':
            target_group = 't.standard_des'
            grouping = 'usage'
        if group_by == 'product_category':
            target_group = 't.category'
            grouping = 'product_category'
        if group_by == 'brand':
            target_group = 't.brand'
            grouping = 'brand'
        if group_by == 'usage':
            target_group = "(CASE WHEN u.usage IS NULL THEN '' ELSE u.usage end)"
            grouping = 'usage'
            join_table = 'JOIN scm_master_list_mc_data u on t.barcode = u.barcode'

        # brand field values
        if self.brand_ids:
            brands = ''
            for x in self.brand_ids:
                if brands:
                    brands += ","
                brands += "'%s'" % (x.brand_name)
            brands = "(%s)" % (brands)
            # insert brand field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' brand IN %s' % brands
            if target_cond:
                target_cond += ' and '
            target_cond += ' t.brand IN %s' % brands

        # fetch branch ids based on user's allowed branches
        branch_codes = self.env['res.users'].sudo().search([('id', '=', self.env.uid)]).get_codes()
        branch_codes.append('0')

        # product field values
        if self.description_ids:
            descriptions = ''
            for x in self.description_ids:
                if descriptions:
                    descriptions += ","
                descriptions += "'%s'" % (x.description_name)
            descriptions = "(%s)" % (descriptions)
            # insert product field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' standard_description IN %s' % descriptions
            if target_cond:
                target_cond += ' and '
            target_cond += ' t.standard_des IN %s' % descriptions

        # product category/group field values
        if self.category_ids:
            categories = ''
            for x in self.category_ids:
                if categories:
                    categories += ","
                categories += "'%s'" % (x.categ_name)
            categories = "(%s)" % (categories)
            # insert product category/group field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' product_category IN %s' % categories
            if target_cond:
                target_cond += ' and '
            target_cond += ' t.category IN %s' % categories

        # area field values
        if self.area_ids:
            areas = ''
            for x in self.area_ids:
                if areas:
                    areas += ","
                areas += "'%s'" % (x.area_name)
            areas = "(%s)" % (areas)
            # insert area field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' area IN %s' % areas
            if target_cond:
                target_cond += ' and '
            target_cond += ' t.area IN %s' % areas

        # branch field values
        if self.branch_ids:
            branches = ''
            for x in self.branch_ids:
                if branches:
                    branches += ","
                branches += "'%s'" % (x.branch_name)
            branches = "(%s)" % (branches)
            # insert branch field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' branch IN %s' % branches
            if target_cond:
                target_cond += ' and '
            target_cond += ' t.branch_name IN %s' % branches

        # usage field values
        if self.usage_ids:
            usages = ''
            for x in self.usage_ids:
                if usages:
                    usages += ","
                usages += "'%s'" % (x.usage_name)
                join_table = 'JOIN scm_master_list_mc_data u on t.barcode = u.barcode'
            usages = "(%s)" % (usages)
            # insert usage field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' usage IN %s' % usages
            if target_cond:
                target_cond += ' and '
            target_cond += ' u.usage IN %s' % usages

        # company field values
        if self.company_ids:
            companies = ''
            for x in self.company_ids:
                if companies:
                    companies += ","
                companies += "'%s'" % (x.company_name)
            companies = "(%s)" % (companies)
            # insert company field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' company IN %s' % companies
            if target_cond:
                target_cond += ' and '
            target_cond += ' t.company_id IN %s' % companies

        # sales type field values
        if self.type_ids:
            types = ''
            for x in self.type_ids:
                if types:
                    types += ","
                types += "'%s'" % (x.type_name)
            types = "(%s)" % (types)
            # insert sales type field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' sales_type IN %s' % types

        # class outlet field values
        if self.outlet_ids:
            outlets = ''
            for x in self.outlet_ids:
                if outlets:
                    outlets += ","
                outlets += "'%s'" % (x.outlet_name)
            outlets = "(%s)" % (outlets)
            # insert class outlet field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' class_outlet IN %s' % outlets

        # customer type field values
        if self.customer_ids:
            customers = ''
            for x in self.customer_ids:
                if customers:
                    customers += ","
                customers += "'%s'" % (x.customer_name)
            customers = "(%s)" % (customers)
            # insert customer type field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' customer_type IN %s' % customers

        # service type field values
        if self.service_ids:
            services = ''
            for x in self.service_ids:
                if services:
                    services += ","
                services += "'%s'" % (x.service_name)
            services = "(%s)" % (services)
            # insert service type field values into SQL query
            if where_cond:
                where_cond += ' and '
            where_cond += ' service_type IN %s' % services


        # multiple filter fields selected
        if where_cond:
            where_cond = 'and ' + where_cond
        if target_cond:
            target_cond = 'and ' + target_cond

        # SQL query to fetch Actual vs Target data
        query2 = f"""with target as
                        (
	                        select {target_group} as field_grp,
	                        SUM(CASE WHEN TO_CHAR(t.month_date, 'YYYY-MM') = TO_CHAR((date('{order_date}')), 'YYYY-MM')
                                THEN t.quantity end) as target_month_qty,
							SUM(CASE WHEN TO_CHAR(t.month_date, 'YYYY-W') = TO_CHAR((date('{order_date}')), 'YYYY-W')
                                THEN t.quantity end) as target_week_qty,
	                        SUM(CASE WHEN TO_CHAR(t.month_date, 'YYYY') = TO_CHAR((date('{order_date}')), 'YYYY')
                                THEN t.quantity end) as target_ytd_qty,
							SUM(CASE WHEN TO_CHAR(t.month_date, 'YYYY-MM') = TO_CHAR((date('{order_date}')), 'YYYY-MM')
                                THEN t.amount end) as target_month_value,
							SUM(CASE WHEN TO_CHAR(t.month_date, 'YYYY-W') = TO_CHAR((date('{order_date}')), 'YYYY-W')
                                THEN t.amount end) as target_week_value,
	                        SUM(CASE WHEN TO_CHAR(t.month_date, 'YYYY') = TO_CHAR((date('{order_date}')), 'YYYY')
                                THEN t.amount end) as target_ytd_value
	                        from mc_barcode t {join_table}
	                        where date(month_date) >= date_trunc('year', (date('{order_date}') - interval '1 year'))
			   				and date(month_date) <= '{order_date}'
							{target_cond}
			  				group by {target_group}
                        ),
                        sales as
                        (
                            select {grouping}, {group_by} as field_grp,
			                SUM(CASE WHEN TO_CHAR(date, 'YYYY-MM') = TO_CHAR((date('{order_date}') - interval '1 month'), 'YYYY-MM')
                                THEN qty end) as actual_last_month_qty,
                            SUM(CASE WHEN TO_CHAR(date, 'YYYY-MM-W') = TO_CHAR((date('{order_date}') - interval '1 week'), 'YYYY-MM-W')
                                THEN qty end) as actual_last_week_qty,
	                        SUM(CASE WHEN TO_CHAR(date, 'YYYY-MM') = TO_CHAR((date('{order_date}') - interval '1 month'), 'YYYY-MM')
                                THEN (amount) end) as actual_last_month_value,
                            SUM(CASE WHEN TO_CHAR(date, 'YYYY-MM-W') = TO_CHAR((date('{order_date}') - interval '1 week'), 'YYYY-MM-W')
                                THEN (amount) end) as actual_last_week_value,
                            SUM(CASE WHEN TO_CHAR(date, 'YYYY-MM') = TO_CHAR((date('{order_date}')), 'YYYY-MM')
                                THEN qty end) as actual_this_month_qty,
                            SUM(CASE WHEN TO_CHAR(date, 'YYYY-MM-W') = TO_CHAR((date('{order_date}')), 'YYYY-MM-W')
                                THEN qty end) as actual_this_week_qty,
	                        SUM(CASE WHEN TO_CHAR(date, 'YYYY-MM') = TO_CHAR((date('{order_date}')), 'YYYY-MM')
                                THEN (amount) end) as actual_this_month_value,
                            SUM(CASE WHEN TO_CHAR(date, 'YYYY-MM-W') = TO_CHAR((date('{order_date}')), 'YYYY-MM-W')
                                THEN (amount) end) as actual_this_week_value,
	                        SUM(CASE WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((date('{order_date}') - interval '1 year'), 'YYYY')
                                THEN qty end) as actual_last_ytd_qty,
	                        SUM(CASE WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((date('{order_date}') - interval '1 year'), 'YYYY')
                                THEN (amount) end) as actual_last_ytd_value,
                            SUM(CASE WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((date('{order_date}')), 'YYYY')
                                THEN qty end) as actual_this_ytd_qty,
	                        SUM(CASE WHEN TO_CHAR(date, 'YYYY') = TO_CHAR((date('{order_date}')), 'YYYY')
                                THEN (amount) end) as actual_this_ytd_value
                                from sales_summary where date(date) >= date_trunc('year', (date('{order_date}') - interval '1 year'))
                                and date(date) <= '{order_date}'
							and branch_id in {tuple(branch_codes)}
							{where_cond}
			 				group by {group_by}, {grouping}
                        )
                        SELECT coalesce(a.field_grp,b.field_grp,'OTHERS') as grp, a.actual_last_month_qty, a. actual_last_week_qty,
			            a.actual_last_month_value, a.actual_last_week_value,
			            a.actual_this_month_qty, a.actual_this_week_qty,
			            a.actual_this_month_value, a.actual_this_week_value,
			            b.target_month_qty, b.target_week_qty,
			            b.target_month_value, b.target_week_value,
			            a.actual_this_ytd_qty, a.actual_this_ytd_value,
			            b.target_ytd_qty, b.target_ytd_value,
			            a.actual_last_ytd_qty, a.actual_last_ytd_value, 
			            (CASE WHEN a.{grouping} IS NOT NULL THEN a.{grouping} ELSE '' END) as grouping
                        from sales a FULL JOIN target b ON a.field_grp = b.field_grp
                        ORDER BY (CASE WHEN (CASE WHEN a.{grouping} IS NOT NULL THEN a.{grouping} ELSE '' END) != ''
                        THEN 0 ELSE 1 END), (CASE WHEN a.{grouping} IS NOT NULL THEN a.{grouping} ELSE '' END) ASC"""

        self.env.cr.execute(query2)
        results2 = self.env.cr.fetchall()
        print(query2,'WWWWWWWWW')
        result2_obj = self.env['sales.list']
        result2_obj.search([]).unlink()

        # loop all Actual vs Target data
        for result2 in results2:
            actual_last_month_qty = result2[1]
            actual_last_week_qty = result2[2]
            actual_this_month_qty = result2[5]
            actual_this_week_qty = result2[6]
            actual_last_month_value = result2[3]
            actual_last_week_value = result2[4]
            actual_this_month_value = result2[7]
            actual_this_week_value = result2[8]
            target_this_month_qty = result2[9]
            target_this_week_qty = result2[10]
            target_this_month_value = result2[11]
            target_this_week_value = result2[12]
            actual_ytd_qty = result2[13]
            actual_ytd_value = result2[14]
            target_ytd_qty = result2[15]
            target_ytd_value = result2[16]

            #  if values for monthly are null
            if actual_last_month_qty is None:
                actual_last_month_qty = 0
            if actual_this_month_qty is None:
                actual_this_month_qty = 0
            if actual_last_month_value is None:
                actual_last_month_value = 0
            if actual_this_month_value is None:
                actual_this_month_value = 0
            if target_this_month_qty is None:
                target_this_month_qty = 0
            if target_this_month_value is None:
                target_this_month_value = 0

            #  if values for weekly are null
            if actual_last_week_qty is None:
                actual_last_week_qty = 0
            if actual_this_week_qty is None:
                actual_this_week_qty = 0
            if actual_last_week_value is None:
                actual_last_week_value = 0
            if actual_this_week_value is None:
                actual_this_week_value = 0
            if target_this_week_qty is None:
                target_this_week_qty = 0
            if target_this_week_value is None:
                target_this_week_value = 0

            #  if values for YTD are null
            if actual_ytd_qty is None:
                actual_ytd_qty = 0
            if actual_ytd_value is None:
                actual_ytd_value = 0
            if target_ytd_qty is None:
                target_ytd_qty = 0
            if target_ytd_value is None:
                target_ytd_value = 0

            # variance formulas for monthly
            variance_qty_month = actual_this_month_qty - actual_last_month_qty
            variance_value_month = actual_this_month_value - actual_last_month_value
            variance_target_qty_month = actual_this_month_qty - target_this_month_qty
            variance_target_value_month = actual_this_month_value - target_this_month_value
            # percentage formulas for monthly
            try:
                percent_actual_vs_target_qty_month = actual_this_month_qty / target_this_month_qty
            except ZeroDivisionError:
                percent_actual_vs_target_qty_month = 0
            try:
                percent_actual_vs_target_value_month = actual_this_month_value / target_this_month_value
            except ZeroDivisionError:
                percent_actual_vs_target_value_month = 0

            # variance formulas for weekly
            variance_qty_week = actual_this_week_qty - actual_last_week_qty
            variance_value_week = actual_this_week_value - actual_last_week_value
            variance_target_qty_week = actual_this_week_qty - target_this_week_qty
            variance_target_value_week =  actual_this_week_value - target_this_week_value
            # percentage formulas for weekly
            try:
                percent_actual_vs_target_qty_week = actual_this_week_qty / target_this_week_qty
            except ZeroDivisionError:
                percent_actual_vs_target_qty_week = 0
            try:
                percent_actual_vs_target_value_week = actual_this_week_value / target_this_week_value
            except ZeroDivisionError:
                percent_actual_vs_target_value_week = 0

            # variance formulas for YTD
            variance_target_ytd_qty = actual_ytd_qty - target_ytd_qty
            variance_target_ytd_value =  actual_ytd_value - target_ytd_value
            # percentage formulas for YTD
            try:
                percent_ytd_actual_vs_target_qty = actual_ytd_qty / target_ytd_qty
            except ZeroDivisionError:
                percent_ytd_actual_vs_target_qty = 0
            try:
                percent_ytd_actual_vs_target_value = actual_ytd_value / target_ytd_value
            except ZeroDivisionError:
                percent_ytd_actual_vs_target_value = 0

            # create Actual vs Target table/tree view
            result2_obj.create({
                'wizard2_id': self.id,
                'grouping': result2[19],
                'grp': result2[0],
                'actual_last_month_qty': result2[1],
                'actual_last_week_qty': result2[2],
                'actual_last_month_value': result2[3],
                'actual_last_week_value': result2[4],
                'actual_this_month_qty': result2[5],
                'actual_this_week_qty': result2[6],
                'actual_this_month_value': result2[7],
                'actual_this_week_value': result2[8],
                'target_this_month_qty': result2[9],
                'target_this_week_qty': result2[10],
                'target_this_month_value': result2[11],
                'target_this_week_value': result2[12],
                'variance_vs_last_month_qty': variance_qty_month,
                'variance_vs_last_month_value': variance_value_month,
                'variance_vs_target_qty_month': variance_target_qty_month,
                'variance_vs_target_value_month': variance_target_value_month,
                'percentage_actual_vs_target_qty_month': percent_actual_vs_target_qty_month,
                'percentage_actual_vs_target_value_month': percent_actual_vs_target_value_month,
                'variance_vs_last_week_qty': variance_qty_week,
                'variance_vs_last_week_value': variance_value_week,
                'variance_vs_target_qty_week': variance_target_qty_week,
                'variance_vs_target_value_week': variance_target_value_week,
                'percentage_actual_vs_target_qty_week': percent_actual_vs_target_qty_week,
                'percentage_actual_vs_target_value_week': percent_actual_vs_target_value_week,
                'actual_ytd_qty': result2[13],
                'actual_ytd_value': result2[14],
                'target_ytd_qty': result2[15],
                'target_ytd_value': result2[16],
                'variance_vs_target_ytd_qty': variance_target_ytd_qty,
                'variance_vs_target_ytd_value': variance_target_ytd_value,
                'percentage_ytd_actual_vs_target_qty': percent_ytd_actual_vs_target_qty,
                'percentage_ytd_actual_vs_target_value': percent_ytd_actual_vs_target_value,
                'actual_ytd_last_year_qty': result2[17],
                'actual_ytd_last_year_value': result2[18],
            })

        # XML ID
        tree2_view_id = self.env.ref('sales_dashboard.sales_list_tree_both').id
        form2_view_id = self.env.ref('sales_dashboard.sale_list_both_form_views').id

        # show either qty based columns or value based columns
        show_qty = show_value = True
        if self.unit_of_measure == 'value':
            show_qty = False
        elif self.unit_of_measure == 'quantity':
            show_value = False

        # show either monthly based columns or weekly based columns
        show_month = show_week = True
        if self.time_series == 'month':
            show_week = False
        elif self.time_series == 'week':
            show_month = False

        # group by if criteria is product or branch
        if self.criteria in ('standard_description', 'branch'):
            contexts = 'grouping'
        else:
            contexts = False

        # fetch wizard input for Excel
        for_excel = self.env.context.get('for_excel', False)
        # generate Excel file
        if for_excel:
            return

        # return tree and form view
        return {
            'name': 'Sales Performance Report: Actual vs Target',
            'res_model': 'sales.list',
            'view_mode': 'tree, form',
            'view_type': 'form',
            'views': [(tree2_view_id, 'tree'), (form2_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'context': {'show_quantity': show_qty, 'show_value': show_value,
                        'show_month': show_month, 'show_week': show_week,
                        'group_by': contexts},
        }