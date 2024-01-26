# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class UoM(models.Model):
    _inherit = 'uom.uom'

    category_id = fields.Many2one(
        'uom.category', 'Category', 
        required=True, 
        ondelete='cascade',
        default=lambda self: self.env['uom.category'].search([('measure_type','=','unit')], limit=1).id,
        help="Conversion between Units of Measure can only occur if they belong to the same category. The conversion will be made based on the ratios."
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', _("You can have only one name per 'Unit of Measure'.")),
    ]
