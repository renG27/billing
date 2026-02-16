from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    billing_plan_id = fields.Many2one('billing.plan', string="Paket Langganan Aktif")