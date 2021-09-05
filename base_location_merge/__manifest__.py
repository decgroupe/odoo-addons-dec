{
    'name': 'Merge Locations',
    'version': '12.0.1.0.0',
    'author': 'DEC, Yann Papouin ',
    'website': 'https://www.decgroupe.com',
    'depends': [
        'base_location',
        'deltatech_merge',
    ],
    'data': [
        'security/res_groups.xml',
        'wizard/merge_res_city.xml',
        'wizard/merge_res_city_zip.xml',
    ],
    'installable': True
}
