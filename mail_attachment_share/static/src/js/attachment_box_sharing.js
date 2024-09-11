
odoo.define("mail_attachment_share/static/src/js/attachment_box_sharing.js", function (require) {
    "use strict";

    var rpc = require("web.rpc");

    const components = {
        AttachmentBox: require("mail/static/src/components/attachment_box/attachment_box.js"),
    };

    const { patch } = require("web.utils");

    patch(
        components.AttachmentBox,
        "mail_attachment_share/static/src/js/attachment_box_sharing.js",
        {
            // --------------------------------------------------------------------------
            // Handlers
            // --------------------------------------------------------------------------
            _onClickShare: function (ev) {
                return this.env.bus.trigger('do-action', {
                    action: 'mail_attachment_share.action_attachment_sharing',
                    options: {
                        additional_context: {
                            default_res_id: this.thread.id,
                            default_res_model: this.thread.model,
                        },
                        on_close: () => {
                            this.trigger('reload', { keepChanges: true });
                        },
                    },
                });
            },

        }
    );
});

