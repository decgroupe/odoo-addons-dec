{
    "name": "French Departments (base_location support)",
    "version": "18.0.1.0.0",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base_location",
        "l10n_fr_base_address_city_department",
    ],
    "data": [
        "view/res_city.xml",
    ],
    "post_init_hook": "set_department_and_state_on_res_city",
    "installable": False,
}
