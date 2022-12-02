{
    'name': 'Project Identification',
    'version': "13.0.1.0.0",
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary':
        "Customize name_search and add project type information "
        "on task",
    'depends': [
        'project_category',
    ],
    'data':
        [
            'data/project_category.xml',
            'views/project_project.xml',
            'views/project_task.xml',
            'views/menu.xml',
        ],
    'installable': True
}
