/* global document */
import {UserSwitch} from "@web/core/user_switch/user_switch";
import {getLastConnectedUsers} from "@web/core/user";
import {patch} from "@web/core/utils/patch";

patch(UserSwitch.prototype, {
    setup() {
        super.setup();
        const users = getLastConnectedUsers();

        // Default UserSwitch behaviour has hidden our Magic Form that uses the
        // same class as the default one. We need to restore its visibility.
        const magic_form = document.querySelector("form.oe_login_form");
        magic_form.classList.toggle("d-none", false);

        // Select the Login Form using the ID we added in the template.
        this.form = document.querySelector("#login-form");
        // Re-display the form if there are more than 1 users.
        this.form.classList.toggle("d-none", users.length > 1);
        // Select the first field
        this.form.querySelector(":placeholder-shown")?.focus();
    },
});
