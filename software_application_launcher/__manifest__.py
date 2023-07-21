{
    "name": "Software Application (launcher)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "software_application",
        "software_license",
        "website_sale",  # for css styles
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/software_application.xml",
        "views/software_application_image.xml",
        "data/software_tag.xml",
    ],
    "installable": True,
}
