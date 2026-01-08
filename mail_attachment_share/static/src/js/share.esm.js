import {Chatter} from "@mail/chatter/web_portal/chatter";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(Chatter.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
    },
    _onShareLink(event) {
        event.preventDefault();
        event.stopPropagation();
        this.action.doAction("mail_attachment_share.action_attachment_sharing", {
            additionalContext: {
                default_res_id: this.state.thread.id,
                default_res_model: this.state.thread.model,
            },
            onClose: async () => {
                await this.updateThreadAttachments();
            },
        });
    },
    async updateThreadAttachments() {
        const attachments = await this.orm.call("ir.attachment", "search_read", [
            [
                ["res_model", "=", this.state.thread.model],
                ["res_id", "=", this.state.thread.id],
            ],
            ["id", "name", "mimetype", "url"],
        ]);
        this.state.thread.attachments = attachments.map((att) => ({
            id: att.id,
            name: att.name,
            mimetype: att.mimetype,
            url: att.url,
        }));
    },
});
