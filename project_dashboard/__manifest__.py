{
    'name': 'Project Dashboard',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin',
    'website': 'https://www.decgroupe.com',
    'summary': "Configure types to be displayed in a dashboard",
    'depends':
        [
            'web_one2many_kanban',
            'project_category',
            'project_task_count',
            'mrp_project',
        ],
    'data':
        [
            'views/assets.xml',
            'views/project_project.xml',
            'views/project_type.xml',
            'views/menu.xml',
        ],
    'qweb': ["static/src/xml/dashboard_actions.xml", ],
    'installable': True
}
