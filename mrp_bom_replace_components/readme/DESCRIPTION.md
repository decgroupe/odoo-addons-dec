Replace BoM components in batch across multiple Bills of Materials at once.

A wizard lets users pick an existing component (product) and a replacement
product, then performs the substitution across all (or a selection of)
BoMs in the background using an asynchronous queue job.

Each affected BoM receives a chatter note that lists every changed BoM line
so that the history of component replacements is fully traceable.

Every `write()` on a BoM is also instrumented: additions, removals, and
changes of key fields (product, quantity, supplier, unit of measure, etc.)
are detected and posted as a formatted chatter message on the BoM record.

## Technical details

`MrpBom.write()` captures a snapshot of all BoM lines before and after the
write using `get_track_state()` / `set_track_state()`.  Differences are
classified as added, removed, or edited lines and posted via
`message_post_with_source()` using QWeb templates defined in
`views/bom_template.xml`.

The replacement wizard (`replace.bom.components`) uses `_read_group()` to
group candidate BoMs by id, then delegates each replacement to a `queue_job`
worker so that large BoM sets are handled without blocking the web process.
