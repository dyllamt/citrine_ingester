from pandas import DataFrame


class PifFrame(DataFrame):
    """
    Extends DataFrame methods for massaging DataFrames into the PIF schema.

    General structure:
        In a PifFrame, System objects are designated by individual rows, and
        their sub-system structure is tracked by uids stored in the index. The
        columns of the frame designate individual Pio objects or singletons
        assigned to particular System attributes, all of which is tracked using
        the column name structure. The values of the frame are reserved for
        "value" fields of Pio objects, or objects assigned directly to System
        attributes.

    Index structure:
        The first level of the index contains the uid of the System object. The
        index second level contains the uids of that Systems's childeren.

    Column structure:
        The first level of the column name designates the System attribute that
        this column is assigned to. The second level is reserved for the "name"
        attribute of the an individual Pio object (if there is no second level,
        then it is infered that the cell value is the entire System attribute).
        Any subsequent levels designate key-value pairs for other Pio fields,
        other than name. Levels are deliniated with "." characters, and
        key-value pairings with ":" characters.

    Example:
    |---------------|------------------------------|
    |   index       |           columns            |
    |self childeren | properties.band_gap.units:eV |
    |---------------|------------------------------|
    |uid  [uid]     | float                        |
    |---------------|------------------------------|
    """

    def assign_column_to_attribute(self, column, attribute='properties'):
        """
        Assign a column to a System attribute by prepending its name.

        Ex:
            'band_gap' --> 'properties.band_gap'

        Args:
            columns (str) Column name to assign to an attribute.
            attribute (str) System attribute to assign columns to.
        """
        existing_columns = self.columns.values
        new_columns = [
            '{}.{}'.format(attribute, i) if i == column
            else i for i in existing_columns]
        self.columns = new_columns

    def assign_field_to_column(self, column, field_name, field_value):
        """
        Assigns a new field to a column by appending its name.

        Ex:
            'properites.band_gap' --> 'properties.band_gap.units:eV'

        Args:
            column (str) Column name to assign field.
            field_name (str) Name of the new field.
            field_value (str) Value of that field. Only strings are supported.
        """
        existing_columns = self.columns.values
        new_columns = [
            '{}.{}:{}'.format(i, field_name, field_value) if i == column
            else i for i in existing_columns]
        self.columns = new_columns

    def to_pif_systems(self, systems):
        """
        Returns the current PifFrame as a list of System objects.

        Args:
            systems (System|list of System) A single System type (applying to
                all rows) or list of System types (one for each row).
        """

    @classmethod
    def from_pif_systems(cls, systems):
        """
        Constructor from a list of pif System objects.

        Args:
            systems (list of System) A list of System instances
        """

        rows = []
        for sys in systems:  # starts at top-level systems
            index = sys.pop('uid')
            childeren = sys.pop('subSystems', None)

            while childeren:

