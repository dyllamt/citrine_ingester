import json
import numpy as np

from copy import deepcopy
from pandas import DataFrame, concat
from pypif import pif

"""
This module implements methods and objects for manipulating System objects in
pandas DataFrames. One feature is the flattening/nesting of sub-Systems.
"""


def popattr(obj, attribute, default=None):
    """
    A pop-like method for object attributes (combines getattr and delattr).

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


def flattened_sub_systems(systems):
    """
    Returns a flat representation of a systems network (exposes sub-Systems).

    Args:
        systems (list of System) Root System objects that may contain
            sub-Systems.

    Returns:
        (list of System) All root System objects and their sub-Systems. The
        sub-System structure is tracked by a System attribute "sub_system_ids".
    """

    # ensures that the original System objects remain unmodified
    systems = deepcopy(systems)

    processed_systems = []
    remaining_systems = systems

    while remaining_systems:

        # obtains a system and its sub_system_ids
        system = remaining_systems.pop()
        sub_system_ids = popattr(system, 'sub_systems', default=[])
        if not sub_system_ids:  # necessary because PIF getters return None
            sub_system_ids = []

        # collects this system along with links to its sub_system_ids
        system.sub_system_ids = [sys.uid for sys in sub_system_ids]
        processed_systems.append(system)

        # adds the discovered sub_system_ids to the remaining_systems
        remaining_systems.extend(sub_system_ids)

    return processed_systems


def nested_sub_systems(systems):
    """
    Returns a nested representation of a systems network (embeds sub-Systems).

    Args:
        systems (list of System) All root System objects and their
            sub-Systems. The subSystem structure should be tracked by a
            System attribute "sub_system_ids".

    Returns:
        (list of System) Root System objects that may contain sub-Systems.
    """

    # ensures that the original System objects remain unmodified
    systems = deepcopy(systems)

    # determines root-level System ids (Systems that are not sub-Systems)
    system_ids = [sys.uid for sys in systems]
    child_ids = [getattr(sys, 'sub_system_ids', []) for sys in systems]
    child_ids = [item for sublist in child_ids for item in sublist]
    root_ids = set(system_ids) - set(child_ids)

    # iterates through all systems and sets their sub-System attributes
    # this iteration will also delete the "sub_system_ids" attributes
    for system in systems:
        child_ids = popattr(system, 'sub_system_ids', default=[])
        sub_systems = [sys for sys in systems if sys.uid in child_ids]
        if sub_systems:
            setattr(system, 'subSystems', sub_systems)

    return [sys for sys in systems if sys.uid in root_ids]


class PifFrame(DataFrame):
    """
    A pandas DataFrame for working with System objects. There are options for
    flattening sub-System networks, so that all Systems are exposed.
    """

    def __init__(self, *args, **kwargs):
        super(PifFrame, self).__init__(*args, **kwargs)

    @classmethod
    def from_pif_systems(cls, systems, expose_sub_systems=True):
        """
        Constructor from a list of PIF System objects.

        Args:
            systems (list of System) A list of System instances.
            expose_sub_systems (bool) Whether to expose nested sub-Systems.

        Returns:
            (PifFrame) A DataFrame representation of those Systems.
        """

        if expose_sub_systems:  # flatten sub-Systems
            systems = flattened_sub_systems(systems)

        df_rows = []
        for system in systems:
            system = json.loads(pif.dumps(system))
            df_rows.append(DataFrame.from_dict([system], orient='columns'))
        df = concat(df_rows, axis=0, sort=False)
        return cls(df)

    def to_pif_systems(self, nest_sub_systems=True):
        """
        Returns the PifFrame instance as a list of System objects.

        Args:
            nest_sub_systems (bool) Whether to nest sub-Systems.

        Returns:
            (list of System) List of system objects in the PIF schema.
        """
        systems = [  # filters for columns that are not null
            {k: v for k, v in m.items() if not (v is np.nan)}
            for m in self.to_dict(orient='rows')]
        systems = pif.loado(systems)  # converts to System objects

        if nest_sub_systems:  # re-packs sub-Systems
            systems = nested_sub_systems(systems)

        return systems


if __name__ == '__main__':
    from xmolsystem import XMolMolecularSystem

    # loads a system
    sys = [XMolMolecularSystem.from_file(
        '../data/data_subset/dsgdb9nsd_000116.xyz')]
    print(sys)

    # loads the system into a DataFrame
    frame = PifFrame.from_pif_systems(sys)
    print(frame[['chemicalFormula', 'uid', 'subSystemIds']].to_string())

    # converts the DataFrame back to System objects
    print(frame.to_pif_systems())
