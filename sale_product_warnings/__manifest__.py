{
    "name": "Sale Warnings",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "category": "Sales",
    "depends": [
        "mail",
        "sale",
        "stock",  # for `responsible_id` field on `product.template`
        "product",
        "product_state_review",
    ],
    "data": [
        "data/mail_activity.xml",
        "data/mail_activity_template.xml",
    ],
    "installable": True,
}
