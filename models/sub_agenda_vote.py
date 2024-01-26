
import logging
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import date, datetime, timedelta, MAXYEAR
import requests
import json
import csv
import os

_logger = logging.getLogger(__name__)


class CreateSubAgendaVote(models.Model):
    _name = 'create.sub.agenda.vote'
    _description = 'Create Sub Agenda Vote'
    _rec_name = 'vote_name'

    sub_agenda_id = fields.Many2one(comodel_name="meeting.sub.agenda", string="Sub Agenda", ondelete='cascade', required=True,
                                 index=True)
    vote_name = fields.Char(string="หัวข้อ", required=True, )
    vote_type_id = fields.Many2one(comodel_name="mt.type.vote", string="ประเภทการลงคะแนน", required=True,)
    create_sub_vote_choice_ids = fields.One2many(comodel_name="create.sub.agenda.vote.choice", inverse_name="create_sub_agenda_id",
                                 string="Create Vote Choice")

    vote_partner_ids = fields.Many2many('res.partner', 'create_sub_agenda_vote_res_partner_rel',
                                        string='ผู้ลงคะแนน')

    start_date = fields.Date(string="วันที่เริ่ม", required=False, default=fields.Date.context_today)
    end_date = fields.Date(string="ถึงวันที่", required=False, default=fields.Date.context_today)

    vote_state = fields.Selection(string="สถานะ", related='sub_agenda_id.vote_state')
    election_id = fields.Char(string="helios vote id")

    @api.onchange('sub_agenda_id')
    def _onchange_sub_agenda_id(self):
        partners_vote = None
        if self.sub_agenda_id:
            partners_vote = self.sub_agenda_id.agenda_id.meeting_id.partner_ids
        result = self.update({'vote_partner_ids': partners_vote})
        return result


class CreateSubAgendaVoteChoice(models.Model):
    _name = 'create.sub.agenda.vote.choice'
    _description = 'Create Agenda Vote choice'
    _rec_name = 'question'
    _order = 'number'

    create_sub_agenda_id = fields.Many2one(comodel_name="create.sub.agenda.vote", string="Create Sub Agenda Vote",
                                       ondelete='cascade', required=True, index=True)

    number = fields.Integer(string="ข้อที่", required=True, )
    question = fields.Text(string="คำถาม", required=True, )
    active = fields.Boolean(string="สถานะ", default=True)

    create_sub_vote_choice_line_ids = fields.One2many(comodel_name="create.sub.agenda.vote.choice.line", inverse_name="create_sub_agenda_id",
                                     string="Create Vote Choice line")

    @api.model
    def create(self, vals):
        question = super(CreateSubAgendaVoteChoice, self).create(vals)

        # create helios vote
        self.create_question_helios(question)
        return question

    @api.model
    def write(self, vals):
        res = super(CreateSubAgendaVoteChoice, self).write(vals)
        if vals:
            # update helios vote
            question = self
            self.create_question_helios(question)
        return res


class CreateSubAgendaVoteChoiceLine(models.Model):
    _name = 'create.sub.agenda.vote.choice.line'
    _description = 'Sub Agenda Vote line'
    _rec_name = 'answer_label'
    _order = 'answer_num'

    create_sub_agenda_id = fields.Many2one(comodel_name="create.sub.agenda.vote.choice", string="Sub Agenda Vote", ondelete='cascade', required=True,
                                 index=True)

    answer_num = fields.Char(string="ลำดับ", required=True, )
    answer_label = fields.Char(string="ตัวเลือก", required=True, )
    answer = fields.Boolean(string="เลือก", required=False, )
    answer_count = fields.Integer(string="จำนวนที่ลงคะแนน", compute='_compute_answer_count', required=False, )

    sub_agenda_vote_line_ids = fields.One2many(comodel_name="sub.agenda.vote.choice.line",
                                                 inverse_name="vote_sub_choice_line_id", string="Sub Vote choice")

    # count of answer
    @api.model
    def _compute_answer_count(self):
        count = 0
        for record in self:
            vote_choices = self.env['sub.agenda.vote.choice.line'].search([('vote_sub_choice_line_id', '=', record.id)])
            # if vote_choices.sub_agenda_id.vote_state == "close":
            if vote_choices:
                count = len(vote_choices)
                record.answer_count = count


# res_partner Vote
class SubAgendaVote(models.Model):
    _name = 'sub.agenda.vote.choice.line'
    _description = 'Sub Agenda Vote line'
    _order = 'create_date'

    vote_sub_choice_line_id = fields.Many2one(comodel_name="create.sub.agenda.vote.choice.line", string="Sub Agenda Vote Line",
                                                ondelete='cascade', required=True, index=True)
    sub_agenda_vote_id = fields.Many2one(comodel_name="create.sub.agenda.vote", string="Create Sub Agenda Vote",)
    vote_question_id = fields.Many2one(comodel_name="create.sub.agenda.vote.choice", store=True, string="Question",)
    sub_agenda_id = fields.Many2one(comodel_name="meeting.sub.agenda", store=True,
                                    related="vote_question_id.create_sub_agenda_id.sub_agenda_id", string="Sub Agenda",)

    vote_choice_id = fields.Char(string='ตัวเลือก',  required=False)
    vote_tr_uuid = fields.Many2one('sub.agenda.vote.secret', string='Agenda Vote Secret',  required=False)

    answer_count = fields.Integer(string="คะแนน", required=False, default=1)
    vote_date = fields.Datetime(string="วันที่ลงคะแนน", required=False, default=fields.Datetime.now)
    signature = fields.Char(string='ลงลายเซ็นต์', required=False)


# USer vote
class SubAgendaVoteSecret(models.Model):
    _name = 'sub.agenda.vote.secret'
    _description = 'Sub Agenda Vote Secret'
    _order = 'create_date'

    sub_agenda_vote_id = fields.Many2one(comodel_name="create.sub.agenda.vote", string="Create Sub Agenda Vote",)
    vote_question_id = fields.Many2one(comodel_name="create.sub.agenda.vote.choice", store=True, string="Question",)

    vote_tr_id = fields.Many2one('res.partner', string='ผู้ลงคะแนน',  required=False)
    vote_user_id = fields.Integer(string='ผู้ใช้งาน',  required=False)
    vote_secret_id = fields.Char(string='secret_id',  required=False)
    iv = fields.Char(string='iv',  required=False)
    signature = fields.Char(string='ลงลายเซ็นต์', required=False)