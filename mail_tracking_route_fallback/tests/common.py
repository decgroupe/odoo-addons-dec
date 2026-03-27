# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

# raw MIME email with a tracking pixel in the HTML body but no thread
# reference headers (no In-Reply-To / References), used to simulate a reply
# whose thread can only be resolved via the tracking pixel fallback
MSG_TRACKING_REPLY_TEMPLATE = """\
Return-Path: <sender@example.com>
Delivered-To: catchall@yourcompany.com
Received: from mail.example.com ([172.22.1.253])
\tby mailserver with LMTP id abc123
\tfor <catchall@yourcompany.com>; Mon, 27 Mar 2026 10:00:00 +0200
Content-Type: multipart/alternative;
 boundary="------------trackingboundary001"
Message-ID: <test-reply-{unique_id}@example.com>
Date: Mon, 27 Mar 2026 10:00:00 +0200
MIME-Version: 1.0
Subject: Re: Test notification
To: catchall@yourcompany.com
From: "Test User" <sender@example.com>

--------------trackingboundary001
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit

This is a reply with no thread reference headers.

--------------trackingboundary001
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: 8bit

<html>
  <body>
    <p>This is a reply with no thread reference headers.</p>
    <img src="http://odoo/mail/tracking/open/{db}/{tracking_id}/{token}/blank.gif"/>
  </body>
</html>
--------------trackingboundary001--
"""
