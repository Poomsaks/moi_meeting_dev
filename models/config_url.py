# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ConfigUrl(models.Model):
    _name = 'config.url'
    _description = 'Config url'
    _rec_name = 'app_name'

    app_name = fields.Char(String='App name', Size=100, required=True)
    url = fields.Char(String='Number', required=True)
    remarks = fields.Text(string='Remark')
    active = fields.Boolean('Active', default=True)
