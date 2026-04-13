# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import logging
from collections import defaultdict

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailGroupMember(models.Model):
    _inherit = "mail.group.member"

    @api.model
    def _get_recipient_data(self, groups):
        """Mimic the _get_recipient_data of mail.followers but for mail group members,
        to prefetch all needed data for qweb rendering in a single query. The result is
        a dict of dicts: {group_id: {member_id: {data}}} where data contains the same
        keys as the one returned by mail.followers._get_recipient_data + some
        additional information (lang, active, share, groups) that are needed for qweb
        rendering and that we want to prefetch.
        """
        res = defaultdict(dict)
        for group in groups:
            res[group.id] = defaultdict(dict)
            for member in group.member_ids:
                follower_data = res[group.id][member.id]
                follower_data.update(
                    {
                        "id": member.id,
                        "uid": None,
                        "email": member.email,
                        "email_normalized": member.email_normalized,
                        "lang": self.env.company.partner_id.lang,
                        "notif": "email",
                        "active": True,
                        "groups": False,
                    }
                )
                # important: always consider group members as share users (less
                # permissive case) , the presence of a `partner_id` will be used to
                # determine if it's a portal (partner only) or internal user (has user)
                # then we will check the actual share status of the related user/partner
                follower_data.update(
                    {
                        "share": True,
                        "ushare": False,
                    }
                )
                if member.partner_id:
                    partner_id = member.partner_id
                    follower_data.update(
                        {
                            "lang": partner_id.lang,
                            "active": partner_id.active,
                            "share": partner_id.partner_share,
                        }
                    )
                    if partner_id.user_ids:
                        user_id = partner_id.user_ids[:1]
                        follower_data.update(
                            {
                                "uid": user_id.id,
                                "notif": user_id.notification_type,
                                "ushare": user_id.share,
                                "groups": set(user_id.groups_id.ids),
                            }
                        )
                # from `mail_followers.py:Followers._get_recipient_data()`
                # additional information
                if follower_data["ushare"]:  # any type of share user
                    follower_data["type"] = "portal"
                elif follower_data[
                    "share"
                ]:  # no user, is share -> customer (partner only)
                    follower_data["type"] = "customer"
                else:  # has a user not share -> internal user
                    follower_data["type"] = "user"
        return res
