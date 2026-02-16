from odoo import models, fields, api
from datetime import datetime, date

class BillableVisit(models.Model):
    _name = 'billable.visit'
    _description = 'Log Transaksi Kunjungan'
    _order = 'date desc, id desc'

    name = fields.Char(string="No Referensi", compute='_compute_name', store=True)
    visit_id = fields.Many2one('medical.visit', string="Sumber Kunjungan", required=True, readonly=True)
    patient_id = fields.Many2one(related='visit_id.patient_id', store=True)
    date = fields.Date(string="Tanggal", related='visit_id.date_visit', store=True)
    company_id = fields.Many2one('res.company', string="Klinik", related='visit_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.billing_plan_id.currency_id')

    # Status Billing
    status = fields.Selection([
        ('billable', 'Valid (Ditagih)'),
        ('flagged', 'Perlu Review (Potensi Masalah)'),
        ('non_billable', 'Tidak Ditagih (Gratis/Invalid)')
    ], default='non_billable', string="Status Tagihan", required=True)
    
    flag_reason = fields.Char(string="Catatan / Isu")
    
    # Nilai Uang
    bill_amount = fields.Monetary(string="Nominal Tagihan", default=0.0)

    @api.depends('visit_id')
    def _compute_name(self):
        for rec in self:
            rec.name = f"BILL/{rec.visit_id.name}"

    def process_billing_logic(self):
        """Logic Utama: Dijalankan oleh Cron Job"""
        for rec in self:
            plan = rec.company_id.billing_plan_id
            if not plan:
                rec.write({'status': 'non_billable', 'flag_reason': 'Klinik belum punya Paket Langganan'})
                continue

            # 1. Jalankan Rules (Validator)
            is_valid = True
            issues = []
            
            # Helper untuk cek rule aktif
            active_rules = plan.rule_ids.mapped('code')

            # RULE A: Status Done
            if 'check_done' in active_rules and rec.visit_id.state != 'done':
                is_valid = False
                issues.append("Status belum Selesai")

            # RULE B: Diagnosa
            if 'check_diagnosis' in active_rules and not rec.visit_id.diagnosis_id:
                is_valid = False
                issues.append("Data Diagnosa Kosong")

            # RULE C: Duplicate Check (Flagged, not Invalid)
            if 'check_duplicate' in active_rules:
                duplicate = self.search_count([
                    ('patient_id', '=', rec.patient_id.id),
                    ('date', '=', rec.date),
                    ('id', '<', rec.id), # Cek record sebelumnya hari ini
                    ('status', '=', 'billable')
                ])
                if duplicate > 0:
                    rec.status = 'flagged' # Masuk Flagged, nanti admin putuskan mau ditagih atau tidak
                    rec.flag_reason = "Kunjungan Ganda di Hari Sama"
                    rec.bill_amount = 0 # Default 0 dulu
                    continue # Skip kalkulasi harga

            # RULE D: Admin Forced Check
            if 'check_admin_finish' in active_rules:
                # Cek user yg terakhir write di visit (asumsi button finish trigger write)
                # Logic sederhana: Cek apakah user punya group dokter
                last_editor = rec.visit_id.write_uid
                if not last_editor.has_group('clinic_core.group_clinic_doctor'):
                    rec.status = 'flagged'
                    rec.flag_reason = f"Diselesaikan oleh Admin ({last_editor.name})"
                    rec.bill_amount = 0
                    continue

            # 2. Keputusan Akhir
            if not is_valid:
                rec.status = 'non_billable'
                rec.flag_reason = ", ".join(issues)
                rec.bill_amount = 0
            else:
                rec.status = 'billable'
                rec.flag_reason = False
                
                # 3. Hitung Harga (Tiering)
                if plan.billing_mode == 'flat':
                    rec.bill_amount = 0 # Flat dibayar bulanan, per visit 0
                else:
                    # Hitung ini pasien ke berapa bulan ini?
                    start_date = rec.date.replace(day=1)
                    current_count = self.search_count([
                        ('company_id', '=', rec.company_id.id),
                        ('date', '>=', start_date),
                        ('date', '<=', rec.date),
                        ('status', '=', 'billable')
                    ])
                    # Cari Tier
                    price = 0
                    for tier in plan.tier_ids:
                        # Logic Tier
                        if tier.max_count == 0: # Unlimited tier
                             if current_count >= tier.min_count:
                                 price = tier.price_unit
                        else:
                             if tier.min_count < current_count <= tier.max_count:
                                 price = tier.price_unit
                                 break
                    rec.bill_amount = price