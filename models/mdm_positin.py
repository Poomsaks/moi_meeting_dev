from odoo import models, fields


class MDMPosition(models.Model):
    _name = 'mdm.position'
    _description = 'MDMPosition'

    name = fields.Char(string='ชื่อตำแหน่ง', required=False)
    code = fields.Char(string='รหัสตำแหน่ง', required=False)
