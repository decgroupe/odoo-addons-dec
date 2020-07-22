from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    HelpdeskTicket = env['helpdesk.ticket']
    MailMessage = env['mail.message']
    cr = env.cr
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
                ref, email_from, state, channel_id
            FROM
                crm_helpdesk;
        """
        )
        max_id = 0
        i = 0
        for val in cr.dictfetchall():
            max_id = max(max_id, val['id'])
            channel_id = False
            if val.get('channel_id') in channel_mapping:
                channel_id = channel_mapping[val.get('channel_id')][1]
            data = {
                'create_uid': val['create_uid'],
                'create_date': val['create_date'],
                'write_date': val['write_date'],
                'write_uid': val['write_uid'],
                'description': val.get('description') or '---',
                'name': val['name'],
                'partner_id': val['partner_id'],
                'partner_name': '---',
                'partner_email': val['email_from'],
                'assigned_date': val['date'],
                'user_id': val['user_id'],
                'channel_id': channel_id and channel_id.id or False,
                'number': "HT{:05d}".format(val['id']),
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
                'closed_date': val['date_closed'],
            }
            print(data)
            ticket.write(data)

            i += 1
            if i == 10:
                break
            # TODO: Seach model and res_id and recreate using messagepost
            messages = MailMessage.search(
                [
                    ('model', '=', 'crm.helpdesk'),
                    ('res_id', '=', val.get('id')),
                ]
            )
            if messages:
                data = {
                    'model': 'helpdesk.ticket',
                    'res_id': ticket.id,
                }
                messages.write(data)

        # Update sequence helpdesk ticket sequence
        sequence = env.ref('helpdesk_mgmt.helpdesk_ticket_sequence')
        sequence.number_next_actual = max(
            sequence.number_next_actual, max_id + 1
        )
