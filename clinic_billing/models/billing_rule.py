from odoo import models, fields

class BillingRule(models.Model):
    _name = 'billing.rule'
    _description = 'Aturan Validasi Tagihan'

    name = fields.Char(required=True)
    code = fields.Selection([
        ('check_done', 'Status Wajib Selesai (Done)'),
        ('check_diagnosis', 'Wajib Ada Diagnosa'),
        ('check_treatment', 'Wajib Ada Obat/Tindakan'),
        ('check_duplicate', 'Cek Kunjungan Ganda Hari Ini'),
        ('check_admin_finish', 'Cek Jika Diselesaikan Admin (Bukan Dokter)')
    ], required=True, string="Logic Code")
    
    active = fields.Boolean(default=True)
    description = fields.Text()