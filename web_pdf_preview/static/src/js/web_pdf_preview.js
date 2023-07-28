odoo.define('web_pdf_preview.Session', function (require) {

    // Warning web.Session if the class, while web.session is the instance
    var Session = require('web.Session');

    Session.include({
        get_file: function (options) {
            const self = this;

            if (options.url === '/report/download') {
                var params = {
                    data: options.data.data,
                    token: new Date().getTime()
                };
                var url = self.url('/report/preview', params);
                return self._open_file(options, url);
            } else {
                // return self._super(options);
                return self._super.apply(self, arguments);
            }
        },

        _open_file: function (options, url) {
            /*
            * Open the PDF report in current window on mobile (since iPhone prevents
            * opening in new window), while open in new window on desktop.
            */
            var result = true;
            if (this._is_mobile()) {
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
        },

        _is_mobile: function () {
            return /Android|iPhone|iPad|iPod|Mobi/i.test(navigator.userAgent);
        },

    });

    return Session;

});
