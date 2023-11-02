Reintroduce sequence field to sort leaves types.
Please note that built-in `hr.leave.type` model hook the `_search` method to manually sort results based on employee data using `_model_sorting_key`.
`sequence` value is also added as the primary key in this tuple.