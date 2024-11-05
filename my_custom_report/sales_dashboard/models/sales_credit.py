# -*- coding: utf-8 -*-
import psycopg2
from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SalesCredit(models.Model):
    _name = 'sales.credit'
    _description = "Sales Credit"
    _rec_name = 'so_number'

    so_line_id = fields.Integer(string='Sales Order Line ID')
    salesteam = fields.Char(string='Sales Team')
    date = fields.Date(string='ORDER DATE')
    salesperson = fields.Char(string='Salesperson')
    agent_name = fields.Char(string='Agent')
    so_number = fields.Char(string='Sales Order No.')
    customer = fields.Char(string='Customer Name')
    product_category = fields.Char(string='CLASSIFICATION')
    brand = fields.Char(string='Brand')
    barcode = fields.Char(string='Barcode')
    standard_description = fields.Char(string='Description')
    usage = fields.Char(string='Usage')
    engine_number = fields.Char(string='Engine No.')
    chassis_number = fields.Char(string='Chassis Number')
    pricelist = fields.Char(string='Pricelist')
    tags = fields.Char(string='Tags')
    payment_term = fields.Char(string='Payment Term')
    qty = fields.Integer(string='Qty')
    cost = fields.Float(string='Cost')
    amount = fields.Float(string='Amount')
    company = fields.Char(string='Company')
    branch_id = fields.Char(string='Branch ID')
    area_code = fields.Char(string='Area')
    color = fields.Char(string='Color')
    invoice_date = fields.Date(string='Invoice Date')
    invoice_name = fields.Char(string='Invoice Name')
    invoice_slip = fields.Char(string='Invoice Slip #')
    invoice_state = fields.Char(string='Invoice State')
    company_id = fields.Char(string='Company ID')
    vendor_id = fields.Char(string='Vendor ID')
    vendor_name =fields.Char(string='Vendor Name')

    # fetch sales cash data
    @api.model
    def _sales_credit(self):
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

        result = self.env['sidecar.config'].search([('is_active', '=', True)], limit=1)

        self.env.cr.execute(f'''CREATE EXTENSION IF NOT EXISTS dblink; 
                                select w.so_line_id, w.branch, w.salesteam, 
                                date(w.date_order), w.salesperson, w.agent_name,
								w.so_number, w.partner_id, w.customer, w.sales_type, 
		                        w.product_id, w.product_category, 
								(CASE WHEN w.barcode LIKE 'SC%' THEN 'SIDECAR'
								ELSE w.brand END) as brand,  w.barcode, 
								(CASE WHEN w.barcode LIKE 'SC%' THEN 'SIDECAR'
								ELSE y.description END) as standard_description, 
								(CASE WHEN w.barcode LIKE 'SC%' THEN 'SIDECAR'
								ELSE y.usage END) as usage, w.status, 
								w.engine_number, w.chassis_number,
								w.pricelist, w.tags, w.payment_term, w.qty,
								(CASE WHEN w.barcode LIKE 'SC%' THEN (w.price_unit/{result.sidecar})
								ELSE y.cost END) as cost,
								w.price_unit, w.company, w.company_id, w.branch_id,
								w.invoice_date, w.inv_name, w.inv_slip, w.state, w.vendor_id, w.vendor_name
                                from dblink('{dbconn}',
'WITH salesperson as (SELECT r.id, s.name from res_users r left join res_partner s
                                    on r.partner_id = s.id),
								sales as (SELECT h.name as company, a.company_id, e.name as branch, c.default_code as barcode,
                                    c.name as rawdesc, c.brand , c.model,
                                    (CASE WHEN c.default_code LIKE ''TR%'' THEN ''TRIMOTOR'' 
									WHEN c.default_code LIKE ''SC%'' THEN ''SIDECAR'' 
									ELSE f.name END) as product_category,
                                    g.name as customer, (CASE WHEN h.name=''EPFC'' 
									THEN ''Installment'' ELSE ''Cash'' END) as sales_type,
                                    (b.date_order + interval ''8 hours'') as date_order, 
									b.name as so_number, a.id as so_line_id, b.id as order_id,
                                    b.awb_agent_id, a.qty_invoiced as qty, a.price_unit, 
									a.invoice_status, b.payment_term_id, b.team_id, b.awb_lot_id,
                                    a.order_partner_id, b.state as status, a.product_id, 
									a.salesman_id, b.pricelist_id, e.lot_stock_id as branch_id
                                    FROM ((sale_order_line a FULL JOIN sale_order b ON a.order_id = b.id)
                                    FULL JOIN (product_template c FULL JOIN product_product d
                                    ON c.id = d.product_tmpl_id) ON a.product_id = d.id), stock_warehouse e,
                                    product_category f, res_partner g, res_company h
                                    WHERE a.company_id IN (3) AND b.state IN (''sale'',''done'')
                                    AND b.warehouse_id = e.id AND c.type = ''product'' AND c.tracking IN (''serial'',''lot'',''none'')
                                    AND c.categ_id = f.id  AND f.name = ''MC'' AND a.order_partner_id = g.id 
									AND a.company_id = h.id AND a.invoice_status = ''invoiced'' 
									AND b.invoice_status = ''invoiced'' AND date(b.date_order) <= now()
									AND g.name NOT LIKE ''EPFC%'' AND e.name LIKE ''EPFC%''
                                    GROUP BY c.default_code, c.name, c.brand, c.model, e.name, f.name, g.name,
                                    b.name, a.id, b.id, h.name, a.qty_invoiced, a.price_unit, b.date_order, b.awb_agent_id,
                                    a.order_partner_id, a.product_id, a.salesman_id, b.team_id, b.awb_lot_id,
									b.payment_term_id, b.pricelist_id, e.lot_stock_id
					                ORDER by b.date_order desc),
                                vendor as (select po.id,po.partner_id AS vendor_id,
                                    rp.name AS vendor_name,po.partner_ref,po.x_studio_po_so_source FROM sale_order so
                                    left JOIN purchase_order po ON so.auto_purchase_order_id = po.id
                                    left JOIN res_partner rp ON po.partner_id = rp.id),
								invoice as (SELECT n.id as invoice_line_id, m.id as invoice_id, m.name as inv_name,
					                m.date as invoice_date, m.inv_slip, m.partner_id, m.invoice_origin, n.quantity, 
					                n.price_unit as amount_total, n.price_unit, n.product_id, m.state, mn.lot_id
					                from account_move m JOIN account_move_line n on m.id = n.move_id
									join stock_move_invoice_line_rel smi on n.id = smi.invoice_line_id
									join stock_move sm on smi.move_id = sm.id
									join stock_move_line mn on sm.id = mn.move_id
					                where m.company_id in (3) and m.state NOT IN (''cancel'') 
									and m.invoice_origin like ''S%'' and m.date is not null
					                and n.parent_state NOT IN (''cancel'') and n.exclude_from_invoice_tab = false
					                GROUP BY n.id, m.id, m.name, m.date, m.inv_slip, m.partner_id, m.team_id, 
					                m.invoice_origin, n.quantity, n.price_unit, n.product_id, m.state, mn.lot_id)
				                select sales.so_line_id, sales.company, sales.company_id, sales.branch, o.name as salesteam, sales.product_id,
					                sales.barcode, sales.rawdesc, sales.brand, sales.model, 
					                sales.product_category, sales.customer, sales.sales_type,
					                sales.date_order, sales.so_number, k.name as agent_name, 
									sales.order_partner_id as partner_id, sales.status,
									p.name as engine_number, p.chassis_number,
									n.name as pricelist, m.name as payment_term, l.name as tags, 
									salesperson.name as salesperson, sales.qty, 
									sales.price_unit, sales.branch_id,
									r.invoice_date, r.inv_name, r.inv_slip, r.state,vendor.vendor_id, vendor.vendor_name
					                from sales left join res_partner k on k.id = sales.awb_agent_id
					                left join sale_order_tag_rel j on sales.order_id = j.order_id
					                left join crm_tag m on m.id = j.tag_id
									left join salesperson on salesperson.id = sales.salesman_id
									left join account_payment_term l on sales.payment_term_id = l.id
									left join product_pricelist n on sales.pricelist_id = n.id
									left join crm_team o on sales.team_id = o.id
									left join sale_order_line_invoice_rel q on sales.so_line_id = q.order_line_id
									right join invoice r on q.invoice_line_id = r.invoice_line_id
									left outer join stock_production_lot p on r.lot_id = p.id
									join vendor ON sales.order_id = vendor.x_studio_po_so_source
					                where m.name NOT LIKE ''%INTER BU'' ')
					            AS w(so_line_id integer, company varchar, company_id integer, branch varchar, salesteam varchar,
					            product_id integer, barcode varchar, rawdesc varchar, brand varchar, model varchar, 
					            product_category varchar, customer varchar,  sales_type varchar, date_order timestamp, 
					            so_number varchar, agent_name varchar, partner_id varchar, 
		                        status varchar, engine_number varchar, chassis_number varchar,
								pricelist varchar, tags varchar, payment_term varchar, 
								salesperson varchar, qty double precision, price_unit numeric, branch_id varchar,
								invoice_date date, inv_name varchar, inv_slip varchar, state varchar,vendor_id integer,vendor_name varchar)
                                left outer join scm_master_list_mc_data y on y.barcode = w.barcode
                                group by w.so_line_id, w.company, w.company_id, w.branch, w.salesteam,
                                w.product_id, w.barcode, w.rawdesc, y.description, w.brand, w.model, y.usage, 
                                w.product_category, w.customer, w.sales_type, w.date_order, w.so_number, 
                                w.agent_name, w.partner_id, w.salesperson, w.status,
								w.engine_number, w.chassis_number, w.pricelist, w.payment_term, 
								w.tags, w.qty, y.cost, w.price_unit, w.branch_id, w.invoice_date, 
                                w.inv_name, w.inv_slip, w.state, w.vendor_id, w.vendor_name
                                ORDER BY w.date_order desc''')
        sales_credit = self.env.cr.fetchall()

        SalesCredit = self.env['sales.credit']
        ids = [id[0] for id in sales_credit]
        SalesCredit.search([('so_line_id', 'not in', ids)]).unlink()

        # loop all sales cash
        for rec in sales_credit:
            # search all sales cash
            s_data = self.env['sales.credit'].search([('so_line_id', '=', rec[0])])
            # check if the sale cash exists
            if s_data:
                s_data.write({'so_line_id': rec[0],
                              'salesteam': rec[2],
                              'date': rec[3],
                              'salesperson': rec[4],
                              'agent_name': rec[5],
                              'so_number': rec[6],
                              'customer': rec[8],
                              'product_category': rec[11],
                              'brand': rec[12],
                              'barcode': rec[13],
                              'standard_description': rec[14],
                              'usage': rec[15],
                              'engine_number': rec[17],
                              'chassis_number': rec[18],
                              'pricelist': rec[19],
                              'tags': rec[20],
                              'payment_term': rec[21],
                              'qty': rec[22],
                              'cost': rec[23],
                              'amount': rec[24],
                              'company': rec[25],
                              'company_id': rec[26],
                              'branch_id': rec[27],
                              'invoice_date': rec[28],
                              'invoice_name': rec[29],
                              'invoice_slip': rec[30],
                              'invoice_state': rec[31],
                              'vendor_id': rec[32],
                              'vendor_name': rec[33]
                              })

            else:
                self.env['sales.credit'].create({'id': self.id,
                                                 'so_line_id': rec[0],
                                                 'salesteam': rec[2],
                                                 'date': rec[3],
                                                 'salesperson': rec[4],
                                                 'agent_name': rec[5],
                                                 'so_number': rec[6],
                                                 'customer': rec[8],
                                                 'product_category': rec[11],
                                                 'brand': rec[12],
                                                 'barcode': rec[13],
                                                 'standard_description': rec[14],
                                                 'usage': rec[15],
                                                 'engine_number': rec[17],
                                                 'chassis_number': rec[18],
                                                 'pricelist': rec[19],
                                                 'tags': rec[20],
                                                 'payment_term': rec[21],
                                                 'qty': rec[22],
                                                 'cost': rec[23],
                                                 'amount': rec[24],
                                                 'company': rec[25],
                                                 'company_id': rec[26],
                                                  'branch_id': rec[27],
                                                  'invoice_date': rec[28],
                                                  'invoice_name': rec[29],
                                                  'invoice_slip': rec[30],
                                                  'invoice_state': rec[31],
                                                  'vendor_id': rec[32],
                                                  'vendor_name': rec[33]

                                                 })