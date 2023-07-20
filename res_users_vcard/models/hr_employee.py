# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import models


class Employee(models.Model):
    _inherit = "hr.employee"

    def _generate_vcard(self):
        self.ensure_one()
        res = "\n".join(
            [
                "BEGIN:VCARD",
                "VERSION:2.1",
                f"FN:{self.name}",
                f"ORG:{self.company_id.name}",
                f"TITLE:{self.job_title}",
                f"EMAIL;TYPE=INTERNET,pref:{self.work_email}",
                f"TEL;TYPE=CELL:{self.mobile_phone}",
                f"TEL;TYPE=WORK:{self.address_id.phone}",
                f"TEL;TYPE=FAX:{self.address_id.fax}",
                f"ADR;TYPE=WORK:;;{self.address_id.street} {self.address_id.street2};{self.address_id.city};;{self.address_id.zip};{self.address_id.country_id.name}",
                f"URL:{self.address_id.website}",
                "END:VCARD",
            ]
        )
        return res
