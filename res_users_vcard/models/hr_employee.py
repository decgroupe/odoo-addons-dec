# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import models


class Employee(models.Model):
    _inherit = "hr.employee"

    def _generate_vcard(self):
        """Generate a VCard string for the employee."""
        self.ensure_one()
        adr = self.address_id
        address = (
            f"ADR;TYPE=WORK:;;{adr.street} {adr.street2}"
            f";{adr.city};;{adr.zip};{adr.country_id.name}"
        )
        res = "\n".join(
            [
                "BEGIN:VCARD",
                "VERSION:2.1",
                f"FN:{self.name}",
                f"ORG:{self.company_id.name}",
                f"TITLE:{self.job_title}",
                f"EMAIL;TYPE=INTERNET,pref:{self.work_email}",
                f"TEL;TYPE=CELL:{self.mobile_phone}",
                f"TEL;TYPE=WORK:{adr.phone}",
                address,
                f"URL:{adr.website}",
                "END:VCARD",
            ]
        )
        return res
