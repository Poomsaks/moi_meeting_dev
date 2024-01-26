from odoo import api, fields, models, _


class MtBoardList(models.Model):
    _name = 'mt.board.list'
    _rec_name = 'display_name'

    partner_id = fields.Many2one(
        comodel_name="res.partner", 
        string="รายชื่อ", 
        required=True,
        domain="[('is_company', '=', False),('active', '=', True)]"
    )

    # firstname = fields.Char(
    #     string="ชื่อคณะกรรมการ",
    #     related="partner_id.firstname",
    # )
    # lastname = fields.Char(
    #     string="นามสกุลคณะกรรมการ",
    #     related="partner_id.lastname",
    # )
    display_name = fields.Char(
        string="ชื่อ", 
        related="partner_id.display_name",
        store=True,
    )

    personal_pos = fields.Char(
        string="ตำแหน่ง", 
        related="partner_id.personal_pos",
    )
    affiliation = fields.Char(
        string="สังกัดฝ่าย", 
        related="partner_id.affiliation",
    )


    _sql_constraints = [
        ('unique_display_name', 'UNIQUE(display_name)', _('ชื่อคณะกรรมการนี้มีในระบบแล้ว !!'))
    ]
