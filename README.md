## pifframes


`PifFrame`s mirror the structure of the PIF schema in a pandas `DataFrame` format. `System` instances are tracked using the frame index, and `subSystems` are handled using multiindex semantics. Attributes of the system instances are specified in the columns. In cases where the type of an attribute is an array of *common objects* (*e.g.* properties contains an array of `Property` instances) the column name is appended with the `name` attribute of that particular common object (*e.g.* `properties.band_gap`).