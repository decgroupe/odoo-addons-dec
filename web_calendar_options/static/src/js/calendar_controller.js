odoo.define('web_calendar_options.CalendarController', function (require) {
    'use strict';

    var CalendarController = require('web.CalendarController');
    CalendarController.include({

        custom_events: _.extend({}, CalendarController.prototype.custom_events, {
            changeOption: '_onChangeOption',
        }),

        /**
         * @private
         * @param {OdooEvent} event
         */
        _onChangeOption: function (event) {
            this.renderer.calendar.setOption(event.data.name, event.data.value);
        },

    });

});
