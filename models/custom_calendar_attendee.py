from odoo import fields, models, api


class CustomCalendarAttendee(models.Model):
    _inherit = "calendar.attendee"

    partner_id = fields.Many2one(comodel_name="res.partner", string="ผู้เข้าประชุม", required=False, )
    name = fields.Char(string="ชื่อ", required=False, related='partner_id.name')
    email = fields.Char(string="อีเมล", required=False, related='partner_id.email')
    phone = fields.Char(string="เบอร์โทร", required=False, related='partner_id.phone')
    STATE_SELECTION = [
        ('needsAction', 'รอดำเนินการ'),
        ('tentative', 'ไม่แน่นอน'),
        ('accepted', 'เข้าร่วมประชุม'),
        ('declined', 'ไม่เข้าร่วมประชุม'),
        ('instead', 'ให้ผู้อื่นเข้าร่วมประชุมแทน'),
    ]

    position_id = fields.Many2one(comodel_name="mdm.position", string="ตำแหน่ง", required=False, )
    state = fields.Selection(STATE_SELECTION, string='Status', readonly=True, default='needsAction',
                             help="Status of the attendee's participation")

    declined_note = fields.Text(string="เหตุผลที่ไม่เข้าร่วม", required=False)
    instead_partner_id = fields.Many2one('res.partner', 'ผู้เข้าประชุมแทน')

    attendee_agenda_ids = fields.One2many(comodel_name="attendee.agenda", inverse_name="attendee_id",
                                          string="Vote")

    is_instead_attendee = fields.Boolean(
        string='เป็นผู้เข้าประชุมแทน',
        default=False,
        readonly=True,
    )

    vote_type = fields.Char(string="ประเภทการ vote", required=False)

    @api.model
    def do_instead(self):
        """ Makes event invitation as Instead. """
        return self.write({'state': 'instead'})


class AttendeeAgenda(models.Model):
    _name = 'attendee.agenda'
    _rec_name = 'agenda_title_name'

    attendee_id = fields.Many2one(comodel_name="calendar.attendee",
                                  string="Attendee", ondelete='cascade', required=True,
                                  index=True)

    agenda_title_name = fields.Char(string="หัวข้อการประชุม", required=False)
    note = fields.Char(string="รายละเอียด", required=False)
    vote_choice_id = fields.Many2one(comodel_name='attendee.vote.choice', string='Question', required=False)
