{
    "name": "Web PDF preview",
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': '''Open PDF report directly in browser''',
    'depends': [
        'base',
        'web',
        'report_aeroo',
    ],
    'data': ['views/web_pdf_preview.xml', ],
    'qweb': [],
    'installable': True
}
