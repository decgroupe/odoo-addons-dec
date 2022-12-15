{
    'name': 'Web Report Workflow',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Report template improvements",
    'depends': [
        'web',
        'company_report',
        'l10n_fr',  # siret
    ],
    'data': ['views/report_templates.xml', ],
    'installable': True
}
