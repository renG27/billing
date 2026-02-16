from odoo import models, fields, api

class BillingPlan(models.Model):
    _name = 'billing.plan'
    _description = 'Paket Langganan'
    _inherit = ['mail.thread']

    name = fields.Char(string="Nama Paket", required=True, tracking=True)
    active = fields.Boolean(default=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    billing_mode = fields.Selection([
        ('flat', 'Bulanan Tetap (Flat)'),
        ('per_visit', 'Per Kunjungan (Pay per Visit)')
    ], default='per_visit', required=True, tracking=True)

    # Opsi Flat
    flat_price = fields.Monetary(string="Harga Bulanan")

    # Opsi Tiered
    tier_ids = fields.One2many('billing.tier', 'plan_id', string="Level Harga (Tiers)")
    
    # Aturan Validasi
    rule_ids = fields.Many2many('billing.rule', string="Syarat Kunjungan Valid")