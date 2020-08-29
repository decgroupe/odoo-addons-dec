odoo.define('web_widget_id.id_field', function (require) {
    'use strict';

    var fieldRegistry = require('web.field_registry');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var AbstractField = require('web.AbstractField');

    var FieldID = AbstractField.extend({
        className: 'o_field_id',
        supportedFieldTypes: ['integer'],
        events: _.extend({}, AbstractField.prototype.events, {
            'click': '_onClick',
        }),

        /**
         * @constructor
         * @see FieldChar.init
         */
        init: function (parent, data, options) {
            this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        start: function () {
            this.$el.append(this.value);
        },

        //--------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------

        /**
         * @private
         * @param {MouseEvent} event
         */
        _onClick: function (event) {
            var self = this;
            if (this.mode === 'readonly' && !this.noOpen) {
                event.preventDefault();
                event.stopPropagation();
                this.$el.select();
                document.execCommand("copy");
            }
        },

    });

    fieldRegistry.add('widget_id', FieldID);

    return FieldID;
});
