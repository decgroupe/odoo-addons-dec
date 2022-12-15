{
    'name': 'Document Page Images-to-attachments',
    'version': "14.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': """Convert base64 inline images to attachments""",
    'depends': [
        'document_page',
        'mail',
    ],
    'data': [
        'views/document_page.xml',
    ],
    'installable': True
}
