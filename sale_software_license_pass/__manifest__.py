{
    "name": "Sale Software License (pass)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
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
