This module provides a reusable wizard pattern to run long actions in a
separate thread and close the popup immediately.

- It lets users start a wizard action without keeping the dialog open while
  the job runs.
- It includes an example wizard that generates random signatures for users,
  mainly for testing and demonstration purposes.

## Technical details

**Threaded wizard base model**

The module defines the transient model `wizard.run` with a `run()` entry point.
`run()` calls `pre_execute()`, starts a Python thread, and returns
`ir.actions.act_window_close` so the wizard closes right away. The thread
executes `_threaded_run()`, which opens a dedicated cursor, rebuilds the
environment with that cursor, then calls `execute()` and commits or rolls back
depending on the outcome.

**Extension contract for custom wizards**

`wizard.run` is designed to be inherited. Child wizards must override
`pre_execute()` and `execute()`. The base implementation raises
`NotImplementedError` to enforce this contract.

**Demonstration implementation**

`wizard.generate_user_random_signature` inherits `wizard.run` and implements
`execute()` by searching users and calling
`res.users.generate_random_signature()`. The helper method in `res.users`
builds a random header, adds generation metadata, converts the text to HTML
with `plaintext2html`, and writes it to the user signature.
