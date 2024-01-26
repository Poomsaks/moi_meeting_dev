from odoo import models, fields


class MDMAttendeeVoteChoice(models.Model):
    _name = 'attendee.vote.choice'
    _description = 'MDMAttendeeVoteChoice'

    name = fields.Char(string="choice")

