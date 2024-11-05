#!/usr/bin/python
from configparser import ConfigParser
import psycopg2
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResAreaConfig(models.Model):
    _name = 'res.area.config'
    _description = "Configuration"
    _rec_name = 'database'

    host = fields.Char(string='Host')
    database = fields.Char(string='DB Name')
    port = fields.Char(string='Port')
    user = fields.Char(string='User')
    password = fields.Char(string='Password')
    active = fields.Boolean(string="Active", default=True)

    def scm_conn(self):
        """ Connect to the PostgreSQL database server """
        conf = self.env['scm.config'].search([('active', '=', True)], limit=1)
        if conf:
            params = {'host':conf.host,
                      'database':conf.database,
                      'port':conf.port,
                      'user':conf.user,
                      'password':conf.password}
            conn = psycopg2.connect(**params)
            return conn

