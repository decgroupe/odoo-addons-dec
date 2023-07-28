odoo.define('web_pdf_preview_aeroo.Session', function (require) {

    var Session = require('web_pdf_preview.Session');

    Session.include({
        get_file: function (options) {
            const self = this;
            if (options.url === '/web/report_aeroo') {
                var params = {
                    report_id: options.data.report_id,
                    record_ids: options.data.record_ids,
                    context: options.data.context,
                    action_context: options.data.action_context,
                    token: new Date().getTime(),
                    debug: true,
                };
                var url = self.url('/report/preview_aeroo', params);
                return self._open_file(options, url);
            } else {
                return self._super(options);
            }
        }
    });

    return Session;

});
