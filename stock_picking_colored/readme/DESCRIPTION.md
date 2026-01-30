This module improves stock picking readability by coloring move lines that
belong to the same procurement group.

- Moves with the same procurement group are displayed with the same row color
  in the picking operations list.
- Different groups receive different colors so operators can quickly identify
  which lines belong together.
- Coloring is only applied when multiple groups are present in the current
  picking lines.

## Technical details

**Computed move colors**

The module extends stock.move with two non-stored computed fields:
list_bg_color and list_fg_color. The compute method groups records by group_id
using _read_group and assigns a deterministic color from a predefined palette
to each non-empty group.

**Form view extension**

The inherited stock picking form view adds the two computed color fields to the
move_ids_without_package list and sets the list colors attribute to map dynamic
foreground and background colors.

**List renderer template patch**

The module extends stock.MovesListRenderer.RecordRow in QWeb to inject
getDynamicColoredStyle(column, record) on row cells. This keeps compatibility
with stock specific list rendering while still applying dynamic row styles.
