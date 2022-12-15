{
    'name': 'Healthchecks Support',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Allow to ping an healthchecks server",
    'depends': ['base', ],
    'data':
        [
            'data/ir_config_parameter.xml',
            'data/ir_cron.xml',
            'security/ir.model.access.csv',
            'views/ir_cron.xml',
        ],
    'installable': True
}
