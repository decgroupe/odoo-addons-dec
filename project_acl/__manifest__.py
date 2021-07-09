{
    'name': 'Project ACL',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'http://www.dec-industrie.com',
    'summary': "Add a new supergroup that allows creating a project",
    'depends': ['project', ],
    'data': [
        'security/project_security.xml',
        'views/project_project.xml',
        'views/project_task.xml',
    ],
    'installable': True
}
