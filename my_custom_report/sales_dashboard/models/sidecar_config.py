# -*- coding: utf-8 -*-
import psycopg2
from odoo import models, fields, api, tools
from odoo.http import content_disposition, request
import io
import xlsxwriter
from xlsxwriter import workbook


class SidecarConfig(models.Model):
    _name = 'sidecar.config'
    _description = "Sidecar Config"
    _rec_name = 'date'

    date = fields.Date(string='Date of Effectivity')
    sidecar = fields.Float(string='Sidecar Divisor')
    is_active = fields.Boolean(string='Active', default='True')