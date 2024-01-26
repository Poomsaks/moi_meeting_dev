from odoo import api, fields, models, _


class MtTypeVote(models.Model):
    _name = 'mt.type.vote'
    _rec_name = 'type_name'

    type_name = fields.Char(string="ชื่อประเภท", required=True)

    type_vote = fields.Selection(string="ประเภทการ Vote",
                                 selection=[('public', 'การลงคะแนนโดยเปิดเผย'), ('private', 'การลงคะแนนลับ')],
                                 required=False, default='public')

    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(type_name)', _('ชื่อประเภทนี้ มีในระบบแล้ว !!'))
    ]

    def copy(self, default={}):
        copied_count = self.search_count(
            [('type_name', '=like', _("สำเนา {}%").format(self.type_name))])
        if not copied_count:
            new_name = _("สำเนา {}").format(self.type_name)
        else:
            new_name = _("สำเนา {} ({})").format(self.type_name, copied_count)
        default['type_name'] = new_name

        return super(MtTypeVote, self).copy(default)
