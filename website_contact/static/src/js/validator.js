
function gcaptcha_callback() {
    var $button = document.getElementById("submit_button");
    $button.disabled = false;
}

function gcaptcha_expired_callback() {
    var $button = document.getElementById("submit_button");
    $button.disabled = true;
}

odoo.define('website_contact.validate', function (require) {
    "use strict";

    require('web.dom_ready');
    var core = require("web.core");

    var _lt = core._lt;

    function validateForm() {

        var $el = document.getElementById("validation");
        var total_size = 0;
        var total_count = 0;

        if (!window.FileReader) { // This is VERY unlikely, browser support is near-universal
            console.log("The file API isn't supported on this browser yet.");
            return;
        }

        var attachment_input = document.getElementById('attachment');
        if (!attachment_input.files) { // This is VERY unlikely, browser support is near-universal
            console.error("This browser doesn't seem to support the `files` property of file inputs.");
        } else {
            total_count = attachment_input.files.length;
            for (let i = 0; i < attachment_input.files.length; i++) {
                total_size += attachment_input.files[i].size;
            }
        }

        if (total_count > 5) {
            $el.innerHTML =
                "<span>" + _lt("Max file count reached: ") + total_count + " files.</span>";
            $('div#validation').show();
            return false;
        }
        else if (total_size > 10 * 1024 * 1024) { // 10MB
            $el.innerHTML =
                "<span>Max size reached: " + Math.round(total_size / 1024 / 1024) + "MB.</span>";
            $('div#validation').show();
            return false;
        }
        else {
            $('div#validation').hide();
            return true;
        }
    }

    var $form = document.getElementById("form_create_message");
    $form.onsubmit = validateForm;

    var $recaptcha = document.getElementById("google_recaptcha");
    if ($recaptcha) {
        gcaptcha_expired_callback();
    }


});

