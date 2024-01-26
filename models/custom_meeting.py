from datetime import timedelta

from odoo import models, fields, _, api


class CustomMeet(models.Model):
    _inherit = 'calendar.event'
    _description = 'Team Meet Details'

    room_id = fields.Many2one(comodel_name="mt.room", string="ห้องประชุม", required=False,
                              domain=[('active', '=', True)])
    root_meeting_id = fields.Many2one(comodel_name="calendar.event", string="Root Meeting", required=False, store=True)

    meeting_root_type = fields.Char('ประห้องประชุม', required=False)
    meet_number = fields.Char('เลขห้องประชุม', required=False)
    meet_name = fields.Char('ประห้องประชุม', required=False)
    meet_url = fields.Char('url ห้องประชุม', required=False)
    meet_passcode = fields.Char('รหัสผ่านห้องประชุม', required=False)
    meeting_state = fields.Selection(
        string="สถานะ",
        selection=[
            ('draft', 'บันทึกร่าง'),
            ('wp', 'รออนุมัติการจอง'),
            ('ap', 'อนุมัติการจอง'),
            ('ip', 'ระหว่างการประชุม'),
            ('summary', 'สรุปรายงานการประชุม'),
            ('sp', 'สิ้นสุดการประชุม'),
            ('cancel', 'ยกเลิกการจอง')],
        default='wp'
    )
    meeting_summary = fields.Char('รายละเอียด', required=False)
    cancel_reason = fields.Char('เหตุผลที่ยกเลิกการจอง', required=False)
    cancel_description = fields.Char('รายละเอียดเพิ่มเติม', required=False)

    ### Add fields ###
    alarms_text = fields.Char(string='การแจ้งเตือน', required=False)
    join_inside = fields.Integer(string='ผู้เข้าร่วมภายใน', default=0)
    join_outside = fields.Integer(string='ผู้เข้าร่วมภายนอก', default=0)
    join_count = fields.Integer(
        string='รวมผู้เข้าร่วมประชุม',
        compute='_compute_join_count',
        store=True,
    )

    president_id = fields.Many2one('res.partner',
                                   string='ประธาน',
                                   required=False
                                   )
    contact_person = fields.Char(string='ผู้ติดต่อ', required=False)
    contact_number = fields.Char(string='เบอร์โทรผู้ติดต่อ', required=False)
    ### End Add fields ###

    agenda_ids = fields.One2many(comodel_name="meeting.agenda", inverse_name="meeting_id", string="วาระการประชุม",
                                 copy=True)
    equipment_ids = fields.One2many(comodel_name="meeting.equipment", inverse_name="meeting_id", string="อุปกรณ์",
                                    required=False, copy=True)
    service_ids = fields.One2many(comodel_name="meeting.services", inverse_name="meeting_id", string="บริการ",
                                  required=False, copy=True
                                  )
    meeting_type_id = fields.Many2one(comodel_name="mt.type.meeting", string="ประเภทการประชุม", required=False)

    attendee_ids = fields.One2many(comodel_name="calendar.attendee", string='ผู้เข้าร่วมการประชุม', required=False)

    attach_ids = fields.One2many(comodel_name="meeting.attach", inverse_name="meeting_id", string="อัพโหลดเอกสาร", )

    start_datetime = fields.Date(string="วันเวลาที่เริ่ม", required=False, default=fields.Date.context_today)
    end_datetime = fields.Date(string="วันเวลาที่สิ้นสุด", required=False, default=fields.Date.context_today)
    start_date = fields.Date(string="วันที่เริ่ม", required=False, default=fields.Date.context_today)
    end_date = fields.Date(string="ถึงวันที่", required=False, default=fields.Date.context_today)

    work_group_id = fields.Many2one(comodel_name="mt.work.group", string="เลือกคณะประชุม", required=False,
                                    domain=[('active', '=', True)])

    all_task_count = fields.Integer("# All Tasks", compute='_compute_all_task_count', store=False)
    task_ids = fields.One2many(comodel_name="project.task", inverse_name="meeting_id",
                               string="งาน")

    in_process_task_count = fields.Integer("# Process Task", compute='_compute_in_process_task_count', store=False)
    all_task_count_store = fields.Integer("# All Tasks", store=True)
    in_process_task_count_store = fields.Integer("# Process Task", store=True)

    ATTENDEE_STATE_SELECTION = [
        ('needsAction', 'รอดำเนินการ'),
        ('tentative', 'ไม่แน่นอน'),
        ('accepted', 'เข้าร่วมประชุม'),
        ('declined', 'ไม่เข้าร่วมประชุม'),
        ('instead', 'ให้ผู้อื่นเข้าร่วมประชุมแทน'),
    ]
    attendee_status = fields.Selection(ATTENDEE_STATE_SELECTION, string='Attendee Status', compute='_compute_attendee')

    parent_id = fields.Many2one(comodel_name="calendar.event", string="Parent Meeting", required=False, index=True,
                                ondelete='cascade', )
    child_ids = fields.One2many(comodel_name='calendar.event', inverse_name='parent_id', string='Child Meeting')
    meeting_no = fields.Integer(string="ครั้งที่", required=False, default=1)
    type_id = fields.Many2one(comodel_name="mt.type.meeting", string="ประเภทการประชุม", required=False)

    project_id = fields.Many2one('project.project', string='โครงการ', store=True, domain=[('active', '=', True)])

    room_admin_id = fields.Many2one(related='room_id.room_admin_id', string="ผู้ดูแลห้องประชุม", required=False, )

    attendee_join_ids = fields.One2many(comodel_name="meeting.attendee.join", inverse_name="meeting_id",
                                        string="ผู้เข้าร่วม",
                                        required=False, )

    requester_id = fields.Many2one('res.partner',
                                   string='เจ้าของห้องประชุม',
                                   help="Technical field to save requester_id"
                                   )
    requester_code = fields.Many2one('res.partner',
                                     string='คนสร้างห้องประชุม',
                                     help="Technical field to save requester_id"
                                     )
    description = fields.Text(string="description", required=False, widget="html")

    @api.depends('task_ids')
    def _compute_in_process_task_count(self):
        count = 0
        for record in self:
            meeting_ids = self.env['calendar.event'].search(
                [('root_meeting_id', '=', self.root_meeting_id.id), ('active', '=', True)])
            if meeting_ids:
                for list_task in meeting_ids:
                    for task in list_task.task_ids:
                        if task.task_state != "close":
                            count += 1

                record.in_process_task_count = count
                record.in_process_task_count_store = count

    @api.depends('task_ids')
    def _compute_all_task_count(self):
        count = 0
        for record in self:
            meeting_ids = self.env['calendar.event'].search(
                [('root_meeting_id', '=', self.root_meeting_id.id), ('active', '=', True)])
            if meeting_ids:
                for list_task in meeting_ids:
                    for task in list_task.task_ids:
                        count += 1

                record.all_task_count = count
                record.all_task_count_store = count

    @api.depends('join_inside', 'join_outside')
    def _compute_join_count(self):
        for record in self:
            record.join_count = record.join_inside + record.join_outside

    @api.model
    def all_task_serie_meeting(self):
        meeting_ids = self.env['calendar.event'].search(
            [('root_meeting_id', '=', self.root_meeting_id.id), ('active', '=', True)])

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
            "domain": [('meeting_id', 'in', meeting_ids.ids), ('active', '=', True)],
            "flags": {"form": {"action_buttons": True}},
        }

    # list of in process task in oe_button
    @api.model
    def in_process_task_serie_meeting(self):
        meeting_ids = self.env['calendar.event'].search(
            [('root_meeting_id', '=', self.root_meeting_id.id), ('active', '=', True)])

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
            "domain": [('meeting_id', 'in', meeting_ids.ids), ('task_state', '!=', 'close'), ('active', '=', True)],
            "flags": {"form": {"action_buttons": True}},
        }

    # Button สร้างห้องประชุมวันถัดไป
    def button_copy_meeting_nextday(self):
        final_date = self.start_datetime + timedelta(days=1)
        final_date = final_date.date()
        result = self.create_meeting_by_recurrent(final_date)

        if result:
            result.remove(self)
            for meeting in result:
                return {
                    "type": "ir.actions.act_window",
                    # "name": "จองห้องประชุม",
                    "res_id": meeting.id,
                    "res_model": "calendar.event",
                    "view_type": "form",
                    "view_mode": "form",
                    # "view_id": False,
                    "target": "current",
                }

    # Function สร้างห้องประชุมโดย set recurrent
    def create_meeting_by_recurrent(self, final_date, rrule_type='daily', chk_pass_all=True):
        self.ensure_one()

        self.write({
            'recurrency': True,
            'rrule_type': rrule_type,
            'interval': 1,
            'end_type': 'end_date',
            'final_date': final_date,
            'month_by': None
        })

        all_recurrent = [self]
        pass_recurrent_ids = []
        recurrent_ids = self.get_recurrent_ids([], order="id asc")
        for recurrent_id in recurrent_ids:
            recurrent = self.browse(recurrent_id)
            if not recurrent.get_meeting_check_true():
                pass_recurrent_ids.append(recurrent_id)

        if chk_pass_all:
            if len(pass_recurrent_ids) == len(recurrent_ids) - 1:
                for recurrent_id in pass_recurrent_ids:
                    recurrent = self.browse(recurrent_id)
                    values = {
                        "end_date_time": recurrent.stop,
                        "stop": recurrent.stop - timedelta(seconds=1),
                    }
                    recurrent = recurrent.detach_recurring_event(values)
                    recurrent.update({
                        "recurrent_id": False,
                        "root_meeting_id": self.id,
                    })
                    all_recurrent.append(recurrent)

                self.recurrency = False
                self._compute_rrule()
                self.env.cr.commit()
            else:
                all_recurrent = None
                self.env.cr.rollback()
        else:
            for recurrent_id in pass_recurrent_ids:
                recurrent = self.browse(recurrent_id)
                values = {
                    "end_date_time": recurrent.stop,
                    "stop": recurrent.stop - timedelta(seconds=1),
                }
                recurrent = recurrent.detach_recurring_event(values)
                recurrent.update({
                    "recurrent_id": False,
                    "root_meeting_id": self.id,
                })
                all_recurrent.append(recurrent)

            self.recurrency = False
            self._compute_rrule()
            self.env.cr.commit()

        return all_recurrent

    # ยกเลิกการจอง ห้องประชุม
    def cancel_meeting(self):
        for record in self:
            record.meeting_state = 'cancel'

    # รออนุมัติการจอง ห้องประชุม
    def request_meeting(self):
        for record in self:
            record.meeting_state = 'wp'

    # อนุมัติการจอง ห้องประชุม
    def approve_meeting(self):
        for record in self:
            record.meeting_state = 'ap'

    # ระหว่างการประชุม
    def do_meeting(self):
        for record in self:
            record.meeting_state = 'ip'

    # สรุปรายงานการประชุม
    def summary_meeting(self):
        for record in self:
            record.meeting_state = 'summary'

    # สิ้นสุดการประชุม
    def end_meeting(self):
        for record in self:
            record.meeting_state = 'sp'

    @api.model
    def project_meeting(self):
        self.ensure_one()
        action = self.env.ref('project.open_view_project_all_config').read()[0]
        action['domain'] = [('id', '=', self.project_id.id)]
        return action


class MeetingAgendaUrl(models.Model):
    _name = 'meeting.agenda.url'

    agenda_id = fields.Many2one(comodel_name="meeting.agenda",
                                string="Meeting", ondelete='cascade', required=True,
                                index=True)
    url_name = fields.Char("URL")


class MeetingAgendaAttach(models.Model):
    _name = 'meeting.agenda.attach'

    agenda_id = fields.Many2one(comodel_name="meeting.agenda",
                                string="Meeting", ondelete='cascade', required=True,
                                index=True)
    attach_user = fields.Many2one(comodel_name="res.partner", string="เจ้าของเอกสาร", required=False)
    attach_user_name = fields.Char(related='attach_user.name')
    attach_type = fields.Char("ชนิดเอกสาร")
    attach_flag = fields.Boolean("สถานะใช้งาน")

    attachment_file = fields.Binary("ชื่อเอกสาร", attachment=True, required=True)
    attachment_name = fields.Char("ชื่อเอกสาร")
    attachment_import_date = fields.Datetime(string='วันที่นำเข้า',
                                             default=lambda self: fields.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class MeetingAgenda(models.Model):
    _name = 'meeting.agenda'
    _rec_name = 'agenda_name'
    _order = 'agenda_no'

    meeting_id = fields.Many2one(comodel_name="calendar.event",
                                 string="Meeting", ondelete='cascade', required=True,
                                 index=True)

    agenda_title_name = fields.Char(string="หัวข้อการประชุม", required=True)
    agenda_name = fields.Many2one(comodel_name="mt.agenda", string="ชื่อหัวข้อการประชุม", required=False,
                                  domain=[('active', '=', True)])
    partner_id = fields.Many2one(comodel_name="res.partner", string="ผู้นำเสนอวาระการประชุม", required=False)
    agenda_no = fields.Char(string="ลำดับ", required=True)

    agenda_detail = fields.Text(string="รายละเอียด", required=False, )
    vote_state = fields.Selection(string="สถานะ",
                                  selection=[('draft', 'รอดำเนินการ'),
                                             ('open', 'เปิดลงคะแนน'),
                                             ('close', 'ปิดลงคะแนน')],
                                  required=False, default='draft')

    agenda_attach_ids = fields.One2many(comodel_name="meeting.agenda.attach", inverse_name="agenda_id",
                                        string="แนบเอกสาร")
    agenda_url_ids = fields.One2many(comodel_name="meeting.agenda.url", inverse_name="agenda_id",
                                     string="แนบ URL")
    sub_agenda_ids = fields.One2many(comodel_name="meeting.sub.agenda", inverse_name="agenda_id",
                                     string="วาระการประชุมย่อย")
    create_vote_ids = fields.One2many(comodel_name="create.agenda.vote", inverse_name="agenda_id",
                                      string="Create Vote")

    attendee_count = fields.Integer(string="Attendee Count", required=False, )

    vote_ids = fields.One2many(comodel_name="common.agenda.vote", inverse_name="agenda_meeting_id",
                               string="Vote")


class MeetingEquipment(models.Model):
    _name = 'meeting.equipment'
    _rec_name = 'equipment_id'

    meeting_id = fields.Many2one(comodel_name="calendar.event",
                                 string="Meeting", ondelete='cascade', required=True,
                                 index=True)
    equipment_id = fields.Many2one(comodel_name="mt.equipment", string="อุปกรณ์", required=True)
    equipment_unit = fields.Char(string="หน่วย", related="equipment_id.equip_unit", required=False, )
    equipment_qty = fields.Integer(string="จำนวน", required=False, )

    _sql_constraints = [
        ('unique_meeting_equipment', 'UNIQUE(meeting_id, equipment_id)', _('มีรายการอุปกรณ์ซ้ำ ในการประชุม !!'))
    ]


class MeetingServices(models.Model):
    _name = 'meeting.services'
    _rec_name = 'service_id'

    meeting_id = fields.Many2one(comodel_name="calendar.event",
                                 string="Meeting", ondelete='cascade', required=True,
                                 index=True)
    service_id = fields.Many2one(comodel_name="mt.service", string="บริการ", required=True, )

    service_unit = fields.Char(string="หน่วย", related="service_id.service_unit", required=False, )

    qty_morning = fields.Integer(string="จำนวน (เช้า)", default=0)
    qty_afternoon = fields.Integer(string="จำนวน (บ่าย)", default=0)
    service_qty = fields.Integer(string="จำนวน", default=0)
    sum_qty = fields.Integer(
        string="จำนวนรวม",
        compute='_compute_sum_qty',
        store=True,
    )

    _sql_constraints = [
        ('unique_meeting_service', 'UNIQUE(meeting_id, service_id)', _('มีรายการบริการซ้ำ ในการประชุม !!'))
    ]

    @api.depends('qty_morning', 'qty_afternoon', 'service_qty')
    def _compute_sum_qty(self):
        for record in self:
            record.sum_qty = record.qty_morning + record.qty_afternoon + record.service_qty

    @api.onchange('qty_morning', 'qty_afternoon')
    def _onchange_morning_afternoon(self):
        if self.qty_morning or self.qty_afternoon:
            result = self.update({
                'service_qty': 0,
            })
            return result

    @api.onchange('service_qty')
    def _onchange_service_qty(self):
        if self.service_qty:
            result = self.update({
                'qty_morning': 0,
                'qty_afternoon': 0,
            })
            return result


class MeetingAttach(models.Model):
    _name = 'meeting.attach'

    meeting_id = fields.Many2one(
        comodel_name="calendar.event",
        string="Meeting",
        ondelete='cascade',
        required=True,
        index=True
    )

    attach_user = fields.Many2one(comodel_name="res.partner", string="เจ้าของเอกสาร", required=False)
    attach_user_name = fields.Char(related='attach_user.name')
    attach_type = fields.Char("ชนิดเอกสาร")
    attach_flag = fields.Boolean("สถานะใช้งาน")

    attachment_note = fields.Char("ชื่อรายการ")
    attachment_file = fields.Binary("ชื่อเอกสาร",
                                    attachment=True,
                                    required=True
                                    )
    attachment_name = fields.Char("ชื่อเอกสาร")
    attachment_import_date = fields.Datetime(
        string='วันที่นำเข้า',
        default=lambda self: fields.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


class MeetingSubAgenda(models.Model):
    _name = 'meeting.sub.agenda'
    _rec_name = 'sub_agenda_name'
    _order = 'sub_agenda_no'

    agenda_id = fields.Many2one(comodel_name="meeting.agenda",
                                string="Agenda", ondelete='cascade', required=True,
                                index=True)

    sub_agenda_no = fields.Char(string="ลำดับ", required=True)
    sub_agenda_name = fields.Char(string="วาระการประชุมย่อย", required=True)
    sub_agenda_detail = fields.Text(string="รายละเอียด", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="ผู้นำเสนอวาระการประชุม", required=False)

    sub_agenda_attach_ids = fields.One2many(comodel_name="meeting.sub.agenda.attach", inverse_name="sub_agenda_id",
                                            string="แนบไฟล์")
    sub_agenda_url_ids = fields.One2many(comodel_name="meeting.sub.agenda.url", inverse_name="sub_agenda_id",
                                         string="แนบ URL")

    create_sub_vote_ids = fields.One2many(comodel_name="create.sub.agenda.vote", inverse_name="sub_agenda_id",
                                          string="Create Sub Vote")

    summary_text = fields.Text(string="มติที่ประชุม", required=False, )

    vote_state = fields.Selection(string="สถานะ",
                                  selection=[('draft', 'รอดำเนินการ'),
                                             ('open', 'เปิดลงคะแนน'),
                                             ('close', 'ปิดลงคะแนน')],
                                  required=False, default='draft')

    @api.model
    def approve_meeting(self):
        result = self.write({'meeting_state': 'ap'})
        return result


class MeetingSubAgendaAttach(models.Model):
    _name = 'meeting.sub.agenda.attach'

    sub_agenda_id = fields.Many2one(comodel_name="meeting.sub.agenda",
                                    string="Sub Agenda", ondelete='cascade', required=True,
                                    index=True)
    attach_user = fields.Many2one(comodel_name="res.partner", string="เจ้าของเอกสาร", required=False)
    attach_user_name = fields.Char(related='attach_user.name')
    attach_type = fields.Char("ชนิดเอกสาร")
    attach_flag = fields.Boolean("สถานะใช้งาน")

    attachment_file = fields.Binary("ชื่อเอกสาร", attachment=True, required=True)
    attachment_name = fields.Char("ชื่อเอกสาร")
    attachment_import_date = fields.Datetime(string='วันที่นำเข้า',
                                             default=lambda self: fields.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class MeetingSubAgendaUrl(models.Model):
    _name = 'meeting.sub.agenda.url'

    sub_agenda_id = fields.Many2one(comodel_name="meeting.sub.agenda",
                                    string="Sub Agenda", ondelete='cascade', required=True,
                                    index=True)

    url_name = fields.Char("URL")


class MeetingSubAgendaUserNote(models.Model):
    _name = 'meeting.sub.agenda.user.note'

    sub_agenda_id = fields.Many2one(comodel_name="meeting.sub.agenda",
                                    string="Sub Agenda", ondelete='cascade', required=True,
                                    index=True)

    partner_id = fields.Many2one(comodel_name="res.partner",
                                 string="รายชื่อ", ondelete='cascade', required=True,
                                 index=True)

    text_note = fields.Text("Text Note")
    html_note = fields.Html("HTML Note")


class MeetingSummary(models.Model):
    _name = 'meeting.summary'
    _rec_name = 'summary_name'

    meeting_id = fields.Many2one(comodel_name="calendar.event",
                                 string="Meeting", ondelete='cascade', required=True,
                                 index=True)
    summary_name = fields.Char(string="หัวข้อ", required=False, )
    summary_text = fields.Text(string="รายละเอียด", required=False, )
    attachment_file = fields.Binary("แนบไฟล์", attachment=True, required=False)
    attachment_name = fields.Char("ชื่อเอกสาร")


class MeetingAttendee(models.Model):
    _name = 'meeting.attendee.join'
    # _rec_name = 'partner_id'

    meeting_id = fields.Many2one(comodel_name="calendar.event",
                                 string="Meeting",
                                 ondelete='cascade',
                                 required=True,
                                 index=True
                                 )
    partner_id = fields.Many2one(comodel_name="res.partner",
                                 string="รายชื่อ",
                                 # ondelete='cascade',
                                 required=True
                                 )
    state = fields.Selection(
        string="สถานะ",
        selection=[('yes', 'เข้าร่วม'), ('no', 'ไม่เข้าร่วม')],
        required=False,
        default=None
    )

    approve_date = fields.Datetime(string="วันเวลาที่เข้าร่วม", required=False, default=None)
    passcode = fields.Char(string="รหัส Passcode", required=False, size=7)
    signature = fields.Char(string="signature", required=False, )
