Provides merge wizards for accounting objects:

- **Account Tags**: merge two or more account tags into one, transferring all
  account associations to the destination tag.
- **Account Taxes**: merge two or more account taxes into one, transferring all
  references (invoice lines, fiscal positions, etc.) to the destination tax.
  The destination tax's repartition lines (invoice and credit note) are
  preserved unchanged; the source taxes' repartition lines are discarded on
  deletion.
