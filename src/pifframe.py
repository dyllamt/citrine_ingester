from pandas import DataFrame
from copy import deepcopy


def popattr(obj, attribute, default=None):
    """
    A pop-like method for object attributes.

    Args:
        obj (object) Target object.
        attribute (str) Target attribute name.
        default (object) Return object if attribute does not exist.

    Returns:
        (object) The attribute value or the default object.
    """
    try:
        attribute_value = getattr(obj, attribute)
        delattr(obj, attribute)
    except AttributeError:
        attribute_value = default
    return attribute_value


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

    @classmethod
    def from_pif_systems(cls, systems):
        """
        Constructor from a list of PIF System objects.

        Args:
            systems (list of System) A list of System instances.
        """

        systems = cls._flatten_sub_systems(systems)
        rows = []
        for system in systems:
            rows.append(dict(system))
        return rows

    def to_pif_systems(self, systems):
        """
        Returns the PifFrame instance as a list of System objects.

        Args:
            systems (System|list of System) A single System type (applying to
                all rows) or list of System types (one for each row).
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

    def _flatten_attributes(system):
        """

        """

    def _nest_attributes(system):
        """
        
        """

    @staticmethod
    def _flatten_sub_systems(systems):
        """
        Returns a flat representation of a systems network.

        Args:
            systems (list of System) Root System objects that may contain
                sub-Systems.

        Returns:
            (list of System) All root System objects and their sub-Systems. The
            sub-System structure is tracked by a System attribute "childeren".
        """

        # ensures that the original systems object remains unmodified
        systems = deepcopy(systems)

        processed_systems = []
        remaining_systems = systems

        while remaining_systems:

            # obtains a system and its childeren
            system = remaining_systems.pop()
            childeren = popattr(system, 'sub_systems', default=[])
            if not childeren:  # necessary because PIF getters return None
                childeren = []

            # collects this system along with links to its childeren
            system.childeren = [sys.uid for sys in childeren]
            processed_systems.append(system)

            # adds the discovered childeren to the remaining_systems
            remaining_systems.extend(childeren)

        return processed_systems

    @staticmethod
    def _nest_sub_systems(systems):
        """
        Returns a nested representation of a systems network.

        Args:
            systems (list of System) All root System objects and their
                sub-Systems. The subSystem structure should be tracked by a
                System attribute "childeren".

        Returns:
            (list of System) Root System objects that may contain sub-Systems.
        """

        # ensures that the original systems object remains unmodified
        systems = deepcopy(systems)

        # determines root-level System ids (Systems that are not sub-Systems)
        system_ids = [sys.uid for sys in systems]
        child_ids = [getattr(sys, 'childeren', []) for sys in systems]
        child_ids = [item for sublist in child_ids for item in sublist]
        root_ids = set(system_ids) - set(child_ids)

        # iterates through all systems and sets their sub-System attributes
        # this iteration will also delete the "childeren" attributes
        for system in systems:
            child_ids = popattr(system, 'childeren', default=[])
            sub_systems = [sys for sys in systems if sys.uid in child_ids]
            if sub_systems:
                setattr(system, 'subSystems', sub_systems)

        return [sys for sys in systems if sys.uid in root_ids]


if __name__ == '__main__':
    from xmolsystem import XMolMolecularSystem
    from pypif import pif

    sys = [XMolMolecularSystem.from_file('../data/dsgdb9nsd_133885.xyz')]
    hi = PifFrame._flatten_sub_systems(sys)
    hi = PifFrame._nest_sub_systems(hi)
    print(hi)
    print(sys)
    print(pif.dumps(hi, indent=2))
