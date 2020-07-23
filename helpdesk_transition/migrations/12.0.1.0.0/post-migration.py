import re
from openupgradelib import openupgrade
from odoo import tools

br = re.compile(r"(\r\n|\r|\n)")  # Supports CRLF, LF, CR


def html_newline(content):
    res = br.sub(r"<br />\n", content)  # \n for sourcecode
    return res


def attach_messages_to_ticket(messages, ticket):
    if ticket.description is None:
        plaintext_description = ''
    else:
        plaintext_description = tools.html2plaintext(ticket.description)
        plaintext_description = plaintext_description.replace("\n", "").strip()
    for message in messages:
        data = {
            'message_type':
                'notification',
            'model':
                'helpdesk.ticket',
            'res_id':
                ticket.id,
            'author_id':
                ticket.user_id and ticket.user_id.partner_id
                and ticket.user_id.partner_id.id,
        }
        message.write(data)
        if message.subject:
            msg = '<p><b>{}</b></p>'.format(message.subject)
            if message.body:
                plaintext_body = tools.html2plaintext(message.body)
                plaintext_body = plaintext_body.replace("\n", "").strip()
                if plaintext_body and plaintext_body != plaintext_description:
                    msg += '<small>{}</small>'.format(
                        html_newline(message.body)
                    )
            message.body = msg


@openupgrade.progress()
def migrate_progress(env, cr):
    HelpdeskTicket = env['helpdesk.ticket']
    HelpdeskTicketReference = env['helpdesk.ticket.reference']
    MailMessage = env['mail.message']
    if openupgrade.table_exists(cr, 'crm_helpdesk'):
        # channel_id: crm.case.channel
        channel_mapping = {
            1:
                (
                    'site web',
                    env.ref('helpdesk_mgmt.helpdesk_ticket_channel_web')
                ),
            2:
                (
                    'téléphone',
                    env.ref('helpdesk_mgmt.helpdesk_ticket_channel_phone')
                ),
            3:
                (
                    'direct',
                    env.ref('helpdesk_mgmt.helpdesk_ticket_channel_other')
                ),
            4:
                (
                    'e-mail',
                    env.ref('helpdesk_mgmt.helpdesk_ticket_channel_email')
                ),
        }
        # state: draft, open, cancel, done, pending to convert to stage_id
        state_mapping = {
            'draft': env.ref('helpdesk_mgmt.helpdesk_ticket_stage_new'),
            'open': env.ref('helpdesk_mgmt.helpdesk_ticket_stage_in_progress'),
            'cancel': env.ref('helpdesk_mgmt.helpdesk_ticket_stage_cancelled'),
            'done': env.ref('helpdesk_mgmt.helpdesk_ticket_stage_done'),
            'pending': env.ref('helpdesk_mgmt.helpdesk_ticket_stage_awaiting'),
        }
        cr.execute(
            """
            SELECT
                id, create_uid, create_date, write_date, write_uid,
                date_closed, description, 
                date, partner_id, user_id, name, date_deadline,
                ref, ref2, email_from, state, channel_id
            FROM
                crm_helpdesk;
        """
        )
        max_id = 0
        debug_counter = 0
        for val in cr.dictfetchall():
            max_id = max(max_id, val['id'])
            number = "HT{:05d}".format(val['id'])
            ticket = HelpdeskTicket.search([
                ('number', '=', number),
            ])
            if not ticket:
                debug_counter += 1
                channel_id = False
                if val.get('channel_id') in channel_mapping:
                    channel_id = channel_mapping[val.get('channel_id')][1]

                description = val.get('description')
                if description:
                    description = html_newline(description)
                else:
                    description = '---'

                data = {
                    'create_uid': val['create_uid'],
                    'create_date': val['create_date'],
                    'write_date': val['write_date'],
                    'write_uid': val['write_uid'],
                    'description': description,
                    'name': val['name'],
                    'partner_id': val['partner_id'],
                    'partner_name': '---',
                    'partner_email': val['email_from'],
                    'assigned_date': val['date'],
                    'user_id': val['user_id'],
                    'channel_id': channel_id and channel_id.id or False,
                    'number': number,
                }
                print(data)
                ticket = HelpdeskTicket.create(data)
                # Update stage
                stage_id = False
                if val.get('state') in state_mapping:
                    stage_id = state_mapping[val.get('state')]
                data = {
                    'stage_id': stage_id and stage_id.id or False,
                }
                print(data)
                ticket.write(data)
                # Override closed date
                data = {
                    'closed_date':
                        val['date_closed'],
                    'last_stage_update':
                        val['write_date'] or val['create_date'],
                }
                print(data)
                ticket.write(data)

            # Search for old messages to re-attach them to this ticket
            messages = MailMessage.search(
                [
                    ('model', '=', 'crm.helpdesk'),
                    ('res_id', '=', val.get('id')),
                ]
            )
            attach_messages_to_ticket(messages, ticket)
            if messages:
                print(number)

            # Create reference to first ref
            for ref_field in ('ref', 'ref2'):
                if val.get(ref_field):
                    data = {
                        'ticket_id': ticket.id,
                        'model_ref_id': val.get(ref_field),
                    }
                    HelpdeskTicketReference.create(data)

            # if debug_counter > 10:
            #     break

        # Update sequence helpdesk ticket sequence
        sequence = env.ref('helpdesk_mgmt.helpdesk_ticket_sequence')
        sequence.number_next_actual = max(
            sequence.number_next_actual, max_id + 1
        )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    migrate_progress(env, cr)