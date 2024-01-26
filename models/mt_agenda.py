from odoo import api, fields, models, _


class MtAgenda(models.Model):
    _name = 'mt.agenda'
    _rec_name = 'agenda_name'

    agenda_name = fields.Char(string="วาระการประชุม", required=True)
    active = fields.Boolean(string="สถานะการใช้งาน", default=True)

    _sql_constraints = [
        ('unique_agenda_name', 'UNIQUE(agenda_name)', _('ชื่อวาระการประชุมนี้มีในระบบแล้ว !!'))
    ]

    def copy(self, default={}):
        copied_count = self.search_count(
            [('agenda_name', '=like', _("สำเนา {}%").format(self.agenda_name))])
        if not copied_count:
            new_name = _("สำเนา {}").format(self.agenda_name)
        else:
            new_name = _("สำเนา {} ({})").format(self.agenda_name, copied_count)
        default['agenda_name'] = new_name

        return super(MtAgenda, self).copy(default)
