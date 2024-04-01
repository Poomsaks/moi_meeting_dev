from odoo import models, fields


class MDMOrganize(models.Model):
    _name = 'mdm.organize'
    _description = 'MDMOrganize'

    code = fields.Char(string='code', required=False)
    ref_code = fields.Char(string='refCode', required=False)
    ref_level_code = fields.Char(string='refLevelCode', required=False)
    name = fields.Char(string='name', required=False)
    full_name = fields.Char(string='fullName', required=False)
    name_en = fields.Char(string='nameEn', required=False)
    full_name_en = fields.Char(string='fullNameEn', required=False)
    level = fields.Char(string='level', required=False)
    level_id = fields.Integer(string='level_id', required=False) #กระทรวง=1 สำนัก or กรม 2 กอง 3





