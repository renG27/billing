{
    'name': 'Clinic SaaS Billing & Subscription',
    'version': '1.0',
    'category': 'Hidden/SaaS',
    'summary': 'Provider Billing System: Menghitung Tagihan ke Owner Klinik',
    'description': """
        Module ini adalah Kalkulator Uang Masuk untuk Provider Sistem (Anda).
        Fitur:
        - Master Plan (Flat vs Tiered/Leveling)
        - Deteksi Kunjungan Valid/Invalid
        - Deteksi Kunjungan Ganda & Admin Force Close
        - Laporan Tagihan Bulanan Transparan
    """,
    'author': 'MH',
    'depends': ['base', 'clinic_medical', 'clinic_core'],
    'data': [
        'security/billing_security.xml',
        'security/ir.model.access.csv',
        'data/billing_data.xml',
        'data/billing_cron.xml',
        'views/menu_items.xml',
        'views/billing_plan_views.xml',
        'views/billable_visit_views.xml',
        'views/res_company_views.xml',
        'report/billing_report_actions.xml',
        'report/billing_statement.xml',
    ],
    'installable': True,
    'application': True,
}