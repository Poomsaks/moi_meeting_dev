from cffi import api
from odoo import models, fields
from odoo.exceptions import ValidationError


class CommonAgendaVote(models.Model):
    _name = 'common.agenda.vote'
    _description = 'Agenda Vote'

    agenda_meeting_id = fields.Many2one(string="Agenda", comodel_name="meeting.agenda", ondelete='cascade', )
    meeting_id = fields.Many2one(string="Meeting", comodel_name="calendar.event",
                                 related="agenda_meeting_id.meeting_id",
                                 store=True,
                                 )
    vote_name = fields.Char(string="หัวข้อ", required=True, )
    vote_type_id = fields.Many2one(comodel_name="mt.type.vote", string="ประเภทการลงคะแนน", required=True, )
    vote_choice_ids = fields.One2many(comodel_name="common.agenda.vote.choice", inverse_name="agenda_vote_id",
                                      string="Question")

    vote_partner_ids = fields.Many2many(comodel_name='res.partner', string='รายชื่อผู้มีสิทธิลงคะแนน')

    start_date = fields.Date(string="วันที่เริ่ม", required=False, default=fields.Date.context_today)
    end_date = fields.Date(string="ถึงวันที่", required=False, default=fields.Date.context_today)

    vote_state = fields.Selection(
        string="สถานะ",
        selection=[('draft', 'รอดำเนินการ'),
                   ('open', 'เปิดลงคะแนน'),
                   ('close', 'ปิดลงคะแนน')],
        required=False,
        default='draft'
    )


class CommonAgendaVoteChoice(models.Model):
    _name = 'common.agenda.vote.choice'
    _description = 'Agenda Vote choice'
    _rec_name = 'question'
    _order = 'number'

    agenda_vote_id = fields.Many2one(comodel_name="common.agenda.vote", string="Agenda Vote",
                                     ondelete='cascade', required=True, index=True)

    agenda_meeting_id = fields.Many2one(comodel_name="meeting.agenda", related="agenda_vote_id.agenda_meeting_id",
                                        store=True, string="Agenda", )

    number = fields.Integer(string="ข้อที่", required=True, )
    question = fields.Text(string="คำถาม", required=True, )
    active = fields.Boolean(string="สถานะ", default=True)

    voted_partner_ids = fields.Many2many(
        'res.partner',
        string='ผู้ลงคะแนนแล้ว'
    )

    vote_choice_line_ids = fields.One2many(
        comodel_name="common.agenda.vote.choice.line",
        inverse_name="agenda_vote_choice_id",
        string="Choice"
    )


class CommonAgendaVoteChoiceLine(models.Model):
    _name = 'common.agenda.vote.choice.line'
    _description = 'Agenda Vote choice line'
    _rec_name = 'answer_label'
    _order = 'answer_num'

    agenda_vote_choice_id = fields.Many2one(comodel_name="common.agenda.vote.choice", string="Question",
                                            ondelete='cascade', required=True, index=True)

    answer_num = fields.Char(string="ลำดับ", required=True, )
    answer_label = fields.Char(string="ตัวเลือก", required=True, )
    answer = fields.Boolean(string="เลือก", required=False, )
    answer_count = fields.Integer(string="จำนวนที่ลงคะแนน", compute='_compute_answer_count', required=False, )

    agenda_vote_line_ids = fields.One2many(
        comodel_name="common.agenda.vote.line",
        inverse_name="vote_choice_line_id",
        string="Vote Line"
    )

    # count of answer
    def _compute_answer_count(self):
        for record in self:
            vote_choices = self.env['common.agenda.vote.line'].search_count([('vote_choice_line_id', '=', record.id)])
            record.answer_count = vote_choices


# res_partner Vote
class CommonAgendaVoteLine(models.Model):
    _name = 'common.agenda.vote.line'
    _description = 'Agenda Vote line'
    _order = 'create_date'

    vote_choice_line_id = fields.Many2one(
        string="Choice",
        comodel_name="common.agenda.vote.choice.line",
        ondelete='cascade',
        required=True,
        index=True
    )
    vote_choice_id = fields.Many2one(
        comodel_name="common.agenda.vote.choice",
        related="vote_choice_line_id.agenda_vote_choice_id",
        string="Question",
    )
    vote_id = fields.Many2one(
        comodel_name="common.agenda.vote",
        related="vote_choice_id.agenda_vote_id",
        string="Agenda Vote",
    )
    agenda_meeting_id = fields.Many2one(
        comodel_name="meeting.agenda",
        related="vote_id.agenda_meeting_id",
        store=True,
        string="Agenda",
    )
    vote_answer = fields.Char(string='ตัวเลือก', required=False)
    vote_point = fields.Integer(string="คะแนน", required=False, default=1)
    vote_date = fields.Datetime(string="วันที่ลงคะแนน", required=False, default=fields.Datetime.now)

    signature = fields.Char(string='ลงลายเซ็นต์', required=False)
    vote_partner_id = fields.Many2one(
        string="ผู้ลงคะแนน",
        comodel_name="res.partner",
        required=False,
    )
    is_anonymous = fields.Boolean(string="ไม่ระบุชื่อ", default=True)

    def _check_can_vote(self, partner_id, vote_choice):
        if vote_choice:
            if partner_id not in vote_choice.agenda_vote_id.vote_partner_ids.ids:
                raise ValidationError("รายชื่อนี้ ไม่อยู่ในผู้มีสิทธิลงคะแนน !!")
            if partner_id in vote_choice.voted_partner_ids.ids:
                raise ValidationError("รายชื่อนี้ ได้ทำการโหวตไปแล้ว !!")
        return True

    def api_check_can_vote(self, partner_id, vote_choice_line_id):
        vote_choice = self.env['common.agenda.vote.choice.line'].sudo().search(
            [('id', '=', vote_choice_line_id)]).agenda_vote_choice_id
        if vote_choice:
            if partner_id not in vote_choice.agenda_vote_id.vote_partner_ids.ids:
                return "รายชื่อนี้ ไม่อยู่ในผู้มีสิทธิลงคะแนน !!"
            if partner_id in vote_choice.voted_partner_ids.ids:
                return "รายชื่อนี้ ได้ทำการโหวตไปแล้ว !!"
        return True
