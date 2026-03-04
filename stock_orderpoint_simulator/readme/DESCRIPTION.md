This module adds a simulator on reordering rules so users can test stock rule values
before applying them.

- Open a simulator directly from an orderpoint form.
- Start from the current on-hand quantity and the rule's existing minimum and
  maximum values.
- Adjust the minimum, maximum, and ordering multiple to see the computed quantity
  to order.
- Apply the selected minimum and maximum values back to the real orderpoint when
  the simulation result is satisfactory.

## Technical details

**Orderpoint integration**

The module extends the stock.warehouse.orderpoint form view with an Open
Simulator button that launches a modal action bound to the orderpoint model.

**Simulation defaults and calculations**

The transient model stock.warehouse.orderpoint.simulator loads its defaults from
the active orderpoint in default_get(). It reads the product's available stock,
copies the current min and max quantities, and initializes the multiple from the
purchase unit of measure ratio. Computed fields then derive the needed quantity,
the remainder against the selected multiple, and the final quantity to order.

**Applying the result**

When the user confirms the wizard, action_apply() writes the simulated minimum
and maximum quantities back to the source orderpoint. The wizard is intended to
help tune replenishment thresholds; it does not create procurements or modify
stock by itself.
