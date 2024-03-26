Send an e-mail when a new lead is created.

We use an automated action (base.automation) triggered with `on_create` to send an email using our dedicated template.

On fetchmail, the message route processing will trigger `message_new` on our model.