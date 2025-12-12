{
    "name": "French Departments (base_address_city support)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base_address_extended",  # was base_address_city
        "l10n_fr_department",
    ],
    "data": [
        "security/ir.model.access.csv",
        "view/res_city.xml",
    ],
    "installable": True,
}
