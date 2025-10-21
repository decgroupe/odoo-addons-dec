# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api
from odoo.tools.progressbar import progressbar as pb


def _get_department_code_corsica(zipcode):
    try:
        zipcode = int(zipcode)
    except ValueError:
        return "20"
    if 20000 <= zipcode < 20200:
        # Corse du Sud / 2A
        code = "2A"
    elif 20200 <= zipcode <= 20620:
        code = "2B"
    else:
        code = "20"
    return code


def _get_department(env, zipcode, country_id):
    fr_country_ids = (
        env["res.country"]
        .search([("code", "in", ("FR", "GP", "MQ", "GF", "RE", "YT"))])
        .ids
    )
    department_id = env["res.country.department"]
    zipcode = zipcode.strip().replace(" ", "")
    if zipcode and len(zipcode) == 5 and country_id and country_id.id in fr_country_ids:
        zipcode = zipcode.rjust(5, "0")
        code = zipcode[0:2]
        if code == "97":
            code = zipcode[0:3]
        if code == "20":
            code = _get_department_code_corsica(zipcode)
        department_id = department_id.search(
            [
                ("code", "=", code),
                ("country_id", "in", fr_country_ids),
            ],
            limit=1,
        )
    return department_id


def set_department_and_state_on_res_city(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        fr_countries = env["res.country"].search(
            [("code", "in", ("FR", "GP", "MQ", "GF", "RE", "YT"))]
        )
        city_ids = env["res.city"].search([("country_id", "in", fr_countries.ids)])
        for city_id in pb(city_ids):
            if city_id.department_id:
                continue
            common_department_id = False
            for zip_id in city_id.zip_ids:
                department_id = _get_department(env, zip_id.name, city_id.country_id)
                if not department_id:
                    continue
                if not common_department_id:
                    common_department_id = department_id
                elif department_id != common_department_id:
                    common_department_id = False
                    break
                if department_id != common_department_id:
                    common_department_id = department_id

            if department_id:
                city_id.department_id = department_id
            if city_id.department_id and not city_id.state_id:
                city_id.state_id = city_id.department_id.state_id

    return
