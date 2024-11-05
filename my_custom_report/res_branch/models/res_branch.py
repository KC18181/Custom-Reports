from odoo import models, fields, api, _
import logging

logger = logging.getLogger(__name__)


class ResBranch(models.Model):
    _name = "res.branch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    company_id = fields.Many2one("res.company", string="Company")
    active = fields.Boolean(string="Active", default=False)

    def add_branches(self):
        query = """
        WITH awb_location AS (
                SELECT 
                    temp_location.name,
                    temp_location.code,
                    temp_location.company_id
                FROM dblink('dbname=muti_live host=172.104.49.92 user=muti_dev password=mutidevreadaccess', '
                    SELECT 
                        CONCAT(loc.complete_name, ''/'', ware.name) AS name, loc.id AS code, loc.company_id
                    FROM stock_location loc
                    INNER JOIN stock_warehouse ware ON ware.lot_stock_id = loc.id
                    WHERE loc.usage = ''internal''
                    AND loc.active = True
                    ') AS temp_location(name varchar, code integer, company_id integer)
                )
		SELECT 
            name,
            code,
            company_id,
            true as active
        FROM awb_location
        """
        self.env.cr.execute(query)
        records = self.env.cr.fetchall()
        Branch = self.env["res.branch"]
        for rec in records:
            branch = Branch.search([("code", "=", rec[1])])
            data = {
                "name": rec[0],
                "code": rec[1],
                "company_id": rec[2],
                "active": rec[3],
            }
            if not branch:
                logger.info(f"res.branch create: {data}")
                Branch.create(data)
            else:
                data.update(id=branch.id)
                logger.info(f"res.branch write: {data}")
                Branch.write(data)

    def get_branch(self):
        for rec in self:
            if rec.active:
                return rec.id, rec.name, rec.code
        return False

    # def init(self):

    #     query = """
    # WITH awb_location AS (
    #     SELECT
    #         temp_location.complete_name,
    #         temp_location.id,
    #         temp_location.company_id
    #     FROM dblink('dbname=muti_live host=172.104.49.92 user=muti_dev password=mutidevreadaccess', '
    #         SELECT
    #             CONCAT(loc.complete_name, ''/'', ware.name) AS complete_name, loc.id, loc.company_id
    #         FROM stock_location loc
    #         INNER JOIN stock_warehouse ware ON ware.lot_stock_id = loc.id
    #         WHERE loc.usage = ''internal''
    #         AND loc.active = True
    #         AND loc.company_id <> 3
    #         ') AS temp_location(complete_name varchar, id integer, company_id integer)
    #     )
    #     INSERT INTO res_branch (name, code, company_id, active)
    #     (SELECT
    #         awbl.complete_name AS name,
    #         awbl.id AS code,
    #         awbl.company_id,
    #         True AS active
    #     FROM awb_location awbl
    #     ORDER BY 1)
    #     ON CONFLICT (code) DO NOTHING;
    #     """
    #     self.env.cr.execute(query)


class ResUsers(models.Model):
    _inherit = "res.users"

    branch_ids = fields.Many2many(
        "res.branch",
        string="Allowed Branches",
        domain=lambda self: [("active", "=", True)],
    )
    branch_id = fields.Many2one(
        "res.branch",
        string="Default Branch",
        domain="[('id', 'in', branch_ids)]",
    )

    def create(self, vals):
        self.clear_caches()
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        self.clear_caches()
        return super(ResUsers, self).write(vals)

    def get_codes(self):
        for rec in self:
            branch_codes = []
            for br in rec.branch_ids:
                branch_codes.append(br.code)

        return branch_codes
