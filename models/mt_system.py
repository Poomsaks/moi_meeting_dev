from odoo import models, fields


class MTSystem(models.Model):
    _name = 'mt.system'
    _description = 'MTSystem'

    system_code = fields.Char(
        string='System_code',
        required=False)
    system_name = fields.Char(
        string='System_name',
        required=False)
    system_url = fields.Char(
        string='System_url',
        required=False)
    api_key = fields.Char(
        string=' api_key',
        required=False)
    api_webhook = fields.Char(
        string=' api_webhook',
        required=False)
    api_create = fields.Char(
        string='Api_create',
        required=False)
    url_create = fields.Char(
        string='Url_create',
        required=False)
