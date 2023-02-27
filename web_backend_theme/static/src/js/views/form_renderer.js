odoo.define('web_backend_theme.FormRenderer', function (require) {
    "use strict";

    var dom = require('web.dom');
    var core = require('web.core');
    var config = require("web.config");

    var FormRenderer = require('web.FormRenderer');

    var _t = core._t;
    var QWeb = core.qweb;

    FormRenderer.include({
        _renderButtonBoxNbButtons: function () {
            var $nb_buttons = this._super.apply(this, arguments);
            if (!config.device.isMobile) {
                $nb_buttons = 16;
            }
            return $nb_buttons;
        },
    });

});