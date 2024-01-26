from odoo import api, fields, models


class custom_project_project(models.Model):
    _inherit = 'project.project'

    date_end = fields.Date(string='กำหนดเสร็จ')
    state = fields.Selection([
        ('active', 'On Time'),
        ('late', 'Late'),
        ('finish', 'Finish'),
    ],
        string="สถานะ")
    meeting_count = fields.Integer("# Meetings", compute='_compute_meeting_count')

    # count of meeting for that project
    @api.model
    def _compute_meeting_count(self):
        count = 0
        for record in self:
            meeting_ids = self.env['calendar.event'].search([])
            if meeting_ids:
                for meeting in meeting_ids:
                    if record.id == meeting.project_id.id:
                        count += 1
            record.meeting_count = count

    @api.model
    def schedule_meeting(self):
        # action = self.env.ref('calendar.action_calendar_event').read()[0]
        # action['domain'] = [('project_id', '=', self.id)]
        # return action
        return {
            "type": "ir.actions.act_window",
            "name": "การประชุม",
            "res_id": self.id,
            "res_model": "calendar.event",
            "view_type": "form",
            "view_mode": "tree,form",
            "view_id": False,
            'views': [(self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_tree').id, 'tree'),
                      (self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_form').id, 'form')],
            "domain": [('project_id', '=', self.id)],
            "flags": {"form": {"action_buttons": True}},
        }

    all_task_count = fields.Integer("# All Tasks", compute='_compute_all_task_count')
    in_process_task_count = fields.Integer("# Process Task", compute='_compute_in_process_task_count')

    # count of meeting for that all_task_count
    @api.model
    def _compute_all_task_count(self):
        count = 0
        for record in self:
            task_ids = self.env['project.task'].search([('active', '=', True)])
            if task_ids:
                for task in task_ids:
                    if record.id == task.project_id.id:
                        count += 1
            record.all_task_count = count

    # count of meeting for that in_process_task_count
    @api.model
    def _compute_in_process_task_count(self):
        count = 0
        for record in self:
            task_ids = self.env['project.task'].search([('active', '=', True)])
            if task_ids:
                for task in task_ids:
                    if record.id == task.project_id.id and task.task_state != 'close':
                        count += 1
            record.in_process_task_count = count

    # list of all task in oe_button
    @api.model
    def all_task(self):
        return {
            "type": "ir.actions.act_window",
            "name": "งานทั้งหมด",
            "res_id": self.id,
            "res_model": "project.task",
            "view_type": "form",
            "view_mode": "tree,form",
            "view_id": False,
            'views': [(self.env.ref('odoo_thai_meeting.task_project_task_view_tree').id, 'tree'),
                      (self.env.ref('odoo_thai_meeting.task_project_task_view_form').id, 'form')],
            "domain": [('project_id', '=', self.id), ('active', '=', True)],
            "flags": {"form": {"action_buttons": True}},
        }

    # list of in process task in oe_button
    @api.model
    def in_process_task(self):
        return {
            "type": "ir.actions.act_window",
            "name": "งานที่ยังไม่ปิด",
            "res_id": self.id,
            "res_model": "project.task",
            "view_type": "form",
            "view_mode": "tree,form",
            "view_id": False,
            'views': [(self.env.ref('odoo_thai_meeting.task_project_task_view_tree').id, 'tree'),
                      (self.env.ref('odoo_thai_meeting.task_project_task_view_form').id, 'form')],
            "domain": [('project_id', '=', self.id), ('task_state', '!=', 'close'), ('active', '=', True)],
            "flags": {"form": {"action_buttons": True}},
        }

    # create meeting
    @api.model
    def create_meeting(self):
        return {
            "type": "ir.actions.act_window",
            "name": "การประชุม",
            "res_model": "calendar.event",
            "view_type": "form",
            "view_mode": "form",
            "view_id": False,
            'views': [(self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_form').id, 'form')],
            'context': {'default_name': 'โครงการ ' + self.name,
                        'default_project_id': self.id},
            'target': 'new',
        }