from odoo import fields,models


class Lead(models.Model):
    _inherit = 'crm.lead'

    pre_call_back_date = fields.Date("Preferred Callback Date")
    call_back_time_from = fields.Float("Callback Time From")
    call_back_time_to = fields.Float("Callback Time To")