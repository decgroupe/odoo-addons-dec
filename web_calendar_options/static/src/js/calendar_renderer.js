odoo.define('web_calendar_options.CalendarRenderer', function (require) {
    'use strict';

    var CalendarRenderer = require('web.CalendarRenderer');
    var Widget = require('web.Widget');
    var core = require('web.core');
    var utils = require('web.utils');
    var _t = core._t;

    // Constants
    var CALENDAR_OPTION_COOKIE = 'webCalOpt_';

    var SidebarOptions = Widget.extend({
        template: 'CalendarView.sidebar.options',
        /**
         * @constructor
         * @param {Widget} parent
         * @param {Object} options
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.title = options.title;
            this.cookieName = options.cookieName;
            this.options = options.options;
            this.sidebar_all_options = [];
        },

        /**
         * @override
         */
        start: function () {
            this._super();
            this.$el.on('click', '.custom-checkbox input', this._onOptionBoolClick.bind(this));
            this.$el.on('change', '.custom-list select', this._onOptionListChange.bind(this));
        },

        saveOptionAsCookie(opt) {
            utils.set_cookie(this.cookieName + opt.name, opt.value);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {MouseEvent} e
         */
        _onOptionListChange: function (e) {
            var $select = $(e.currentTarget);
            var opt = {
                'name': $select.closest('.o_calendar_option_item').data('name'),
                'value': $select[0].value,
            };
            this.saveOptionAsCookie(opt);
            this.trigger_up('changeOption', opt);
        },

        /**
         * @private
         * @param {MouseEvent} e
         */
        _onOptionBoolClick: function (e) {
            var $input = $(e.currentTarget);
            var opt = {
                'name': $input.closest('.o_calendar_option_item').data('name'),
                'value': $input.prop('checked'),
            };
            this.saveOptionAsCookie(opt);
            this.trigger_up('changeOption', opt);
        },

    });


    CalendarRenderer.include({
        _initCalendar: function () {

            var nowIndicatorCookie = utils.get_cookie(this.get_cookie_name() + "nowIndicator");
            if (nowIndicatorCookie == "true") {
                nowIndicatorCookie = true;
            } else if (nowIndicatorCookie == "false") {
                nowIndicatorCookie = false;
            } else {
                // Default value
                nowIndicatorCookie = true;
            }

            var weekendsCookie = utils.get_cookie(this.get_cookie_name() + "weekends");
            if (weekendsCookie == "true") {
                weekendsCookie = true;
            } else if (weekendsCookie == "false") {
                weekendsCookie = false;
            } else {
                // Default value
                weekendsCookie = false;
            }

            var slotDurationCookie = utils.get_cookie(this.get_cookie_name() + "slotDuration");
            if (slotDurationCookie == "") {
                // Default value
                slotDurationCookie = '00:30:00';
            }
            var snapDurationCookie = utils.get_cookie(this.get_cookie_name() + "snapDuration");
            if (snapDurationCookie == "") {
                // Default value
                snapDurationCookie = '00:15:00';
            }

            $.extend(this.state.fc_options, {
                weekends: weekendsCookie,
                nowIndicator: nowIndicatorCookie,
                slotDuration: slotDurationCookie,
                snapDuration: snapDurationCookie,
                weekNumberTitle: _t('W'),
                businessHours: {
                    daysOfWeek: [1, 2, 3, 4],
                    start: '08:30',
                    end: '17:00',
                }
            });
            this._super.apply(this, arguments);
        },

        _render: function () {
            var res = this._super.apply(this, arguments);
            this._renderOptions();
            return res;
        },

        get_option(name) {
            var option = this.$calendar.fullCalendar('option', name);
            if (option === undefined) {
                console.warn('get_option', name, option);
            }
            return option;
        },    
        
        get_cookie_name() {
            return CALENDAR_OPTION_COOKIE + this.model + '_';
        },

        _renderOptions: function () {
            var self = this;
            _.each(this.sidebar_all_options || (this.sidebar_all_options = []), function (sidebar_options) {
                sidebar_options.destroy();
            });

            var slotIntervals = [
                ['00:05:00', _t('5 minutes')],
                ['00:10:00', _t('10 minutes')],
                ['00:15:00', _t('15 minutes')],
                ['00:30:00', _t('30 minutes')],
                ['01:00:00', _t('1 hour')],
            ]

            var options = {
                title: _t('Options'),
                cookieName: this.get_cookie_name(),
                options: [
                    {
                        type: 'boolean',
                        label: _t('Now Indicator'),
                        name: 'nowIndicator',
                        default_value: this.get_option('nowIndicator'),
                    },
                    {
                        type: 'boolean',
                        label: _t('Show Weekend'),
                        name: 'weekends',
                        default_value: this.get_option('weekends'),
                    },
                    {
                        type: 'list',
                        label: _t('Slot Duration'),
                        name: 'slotDuration',
                        values: slotIntervals,
                        default_value: this.get_option('slotDuration'),
                    },
                    {
                        type: 'list',
                        label: _t('Snap Duration'),
                        name: 'snapDuration',
                        values: slotIntervals,
                        default_value: this.get_option('snapDuration'),
                    },
                ],
            };
            var sidebar_options = new SidebarOptions(self, options);
            sidebar_options.appendTo(self.$sidebar);
            self.sidebar_all_options.push(sidebar_options);
        },

    });

});
