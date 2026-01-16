{
    "name": "Sale Software License (pass)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "sale_timesheet",
        "sale_project",
        "software_license_pass",
        "partner_commercial_fencing",
    ],
    "data": [
        "views/software_license_pass.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
        "data/mail_template.xml",
    ],
    "demo": [
        "demo/product.xml",
        "demo/sale_order.xml",
    ],
    "installable": True,
}
