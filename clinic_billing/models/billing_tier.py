from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BillingTier(models.Model):
    _name = 'billing.tier'
    _description = 'Level Harga (Tiering)'
    _order = 'min_count asc'

    plan_id = fields.Many2one('billing.plan', required=True)
    currency_id = fields.Many2one(related='plan_id.currency_id')
    
    min_count = fields.Integer(string="Mulai Pasien Ke-", required=True, default=0)
    max_count = fields.Integer(string="Sampai Pasien Ke-", help="Isi 0 jika Unlimited (Level Terakhir)")
    
    price_unit = fields.Monetary(string="Harga per Visit", required=True)

    @api.constrains('min_count', 'max_count')
    def _check_overlap(self):
        for rec in self:
            if rec.max_count > 0 and rec.min_count >= rec.max_count:
                raise ValidationError(f"Range tidak valid pada Tier {rec.min_count}-{rec.max_count}")