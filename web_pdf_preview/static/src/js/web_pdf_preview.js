odoo.define('report.web_pdf_preview', function (require) {

    function is_mobile() {
        return /Android|iPhone|iPad|iPod|Mobi/i.test(navigator.userAgent);
    }

    /*
     * Hook 'session.get_file' to prevent downloading.
     */
    var session = require('web.session');
    var get_file = session.get_file;

    session.get_file = function (options) {
        if (!options || ['/report/download', '/web/report_aeroo'].indexOf(options.url) < 0) {
            return get_file.apply(this, arguments);
        }

        switch (options.url) {
            case '/report/download':
                var params = {
                    data: options.data.data,
                    token: new Date().getTime()
                };
                var url = session.url('/report/preview', params);
                break;
            case '/web/report_aeroo':
                var params = {
                    report_id: options.data.report_id,
                    record_ids: options.data.record_ids,
                    context: options.data.context,
                    action_context: options.data.action_context,
                    token: new Date().getTime(),
                    debug: true,
                };
                var url = session.url('/report/preview_aeroo', params);
                break;
        }

        /*
         * Open the PDF report in current window on mobile (since iPhone prevents
         * opening in new window), while open in new window on desktop.
         */

        var result = true;
        if (is_mobile()) {
            require('web.framework').unblockUI();
            location.href = url;
        } else {
            var w = window.open(url);
            if (w) {
                w.document.title = '...';
                if (typeof options.success === 'function') {
                    options.success();
                }
            } else {
                result = false;
            }
            if (typeof options.complete === 'function') {
                options.complete();
            }
        }
        return result;
    };

});
