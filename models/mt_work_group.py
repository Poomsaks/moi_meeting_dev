from odoo import api, fields, models, _


# @TODO remove
class MtWorkGroup(models.Model):
    _name = 'mt.work.group'
    _rec_name = 'work_group_name'

    work_group_name = fields.Char(string="ชื่อคณะกรรมการ", required=True)
    work_group_last_mame = fields.Char(string="สกุลคณะกรรมการ", required=False)
    work_group_doc = fields.Char(string="เลขที่หนังสือ", required=False)
    work_group_type = fields.Selection(string="ประเภทคณะกรรมการ",
                                       selection=[('1', 'คณะทำงาน'), ('2', 'คณะกรรมการ'), ('3', 'คณะอนุกรรมการ')],
                                       required=False, default='1')
    position_id = fields.Many2one(comodel_name='mdm.position', string='ตำแหน่ง')
    active = fields.Boolean(string="สถานะการใช้งาน", default=True)

    agenda_ids = fields.One2many(comodel_name="mt.work.group.agenda", inverse_name="group_id", string="วาระการประชุม",
                                 copy=False, )
    personal_ids = fields.One2many(comodel_name="mt.work.group.detail", inverse_name="group_id", string="รายชื่อสมาชิก",
                                   copy=False, )

    _sql_constraints = [
        ('unique_work_group_name', 'UNIQUE(work_group_name)', _('ชื่อคณะกรรมการนี้มีในระบบแล้ว !!'))
    ]

    def copy(self, default={}):
        copied_count = self.search_count(
            [('work_group_name', '=like', _("สำเนา {}%").format(self.work_group_name))])
        if not copied_count:
            new_name = _("สำเนา {}").format(self.work_group_name)
        else:
            new_name = _("สำเนา {} ({})").format(self.work_group_name, copied_count)
        default['work_group_name'] = new_name

        return super(MtWorkGroup, self).copy(default)


class MtWorkGroupAgenda(models.Model):
    _name = 'mt.work.group.agenda'
    _order = 'agenda_no'

    group_id = fields.Many2one(comodel_name="mt.work.group",
                               string="คณะกรรมการ", ondelete='cascade', required=True,
                               index=True)

    agenda_id = fields.Many2one(comodel_name="mt.agenda", string="ชื่อหัวข้อการประชุม", required=True,
                                domain=[('active', '=', True)])
    agenda_no = fields.Integer(string="ลำดับ", required=True)


class MtWorkGroupDetail(models.Model):
    _name = 'mt.work.group.detail'
    _order = 'pos_work_no'

    group_id = fields.Many2one(comodel_name="mt.work.group",
                               string="คณะกรรมการ", ondelete='cascade', required=True,
                               index=True)

    personal_id = fields.Many2one(comodel_name="res.partner", string="ชื่อ-นามสกุล", required=True, )
    personal_pos = fields.Char(string="ตำแหน่ง", related='personal_id.personal_pos', required=False)
    pos_work_id = fields.Many2one(comodel_name="mt.pos.work", string="ตำแหน่งประชุม", required=False,
                                  domain=[('active', '=', True)])
    pos_work_no = fields.Integer(string="ลำดับ", related='pos_work_id.pos_no', store=True)
    personal_email = fields.Char(string="อีเมล", required=False)

    @api.onchange('personal_id')
    def _onchange_personal_id(self):
        if self.personal_id:
            self.personal_email = self.personal_id.email
