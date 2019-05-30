import numpy as np

from uuid import uuid4

from pypif.obj import *
from pypif import pif

from pymatgen.core.composition import Composition


"""
This module defines methods for extracting ChemicalSystems from XMol XYZ files.
"""


COMMENTS_BLOCK_LABELS = np.loadtxt(
    'xmol_comments_block_labels.txt', dtype=str)[:, 1:]
# units and labels for the properties in the comments block


class XMolAtomicSystem(ChemicalSystem):
    """
    Representation of an atomic sub-system in an XMol XYZ file.

    System Attributes:
        uid (str) Unique identifier for the system.
        chemical_formula (str) An elemental abbreviation.
        properties (list of dict) Recored properties for the system.

    System Properties:
        position (list of float) The position vector (in Angstroms).
        mulliken_charge (float) Charge on the element (in electrons).
    """
    @classmethod
    def from_molecular_line(cls, line):
        """
        Constructor from a molecular block line in an XMol file.

        Args:
            line (list of str) Line from the molecular block.
        """
        uid = uuid4().hex

        chemical_formula = line[0]                # elemental string
        position = [float(i) for i in line[1:4]]  # position vector
        mulliken_charge = float(line[4])          # scalar charge
        return cls(
            uid=uid, chemical_formula=chemical_formula,
            properties=[{'name': 'position', 'units': 'Angstroms',
                         'value': position},
                        {'name': 'mulliken_charge', 'units': 'electrons',
                         'value': mulliken_charge}])


class XMolMolecularSystem(ChemicalSystem):
    """
    Representation of a molecular system from an XMol XYZ file.

    System Attributes:
        uid (str) Unique identifier for the system.
        chemical_formula (str) Composition of the molecule.
        references (list of dict) Reference to the data source.
        ids (list of str) Ids associated with this molecule.
            id_number (str) Molecule number from the dataset.
            gdb9_string (str) gdb designation.
            smiles_gdb17 (str) SMILES string from GDB-17.
            smiles_b3lyp (str) SMILES string from B3LYP relaxation.
            inchl_corina (str) InChl string for Corina geometry.
            inchl_b3lyp (str) InChl string for B3LYP geometry.
        sub_systems (list of XMolAtomicSystem) The atomic sub-systems that make
            up the molecular system.
        properties (list of dict) Recored properties for the system.

    System Properties (see xmol_comments_block_labels.txt) plus:
        vibrational_frequencies (list of float) Harmonic frequencies (in 1/cm).
    """
    @classmethod
    def from_file(cls, file):
        """
        Constructor from an XMol file path.

        Args:
            file (str) Path to an XMol XYZ file.
        """
        uid = uuid4().hex

        # parses the file into blocks
        with open(file, 'r') as fh:
            file_blocks = cls._parse_file_blocks(fh)

        # constructs atomic sub-systems from the molecule block
        molecule_block = file_blocks.pop('molecule')
        sub_systems = [
            XMolAtomicSystem.from_molecular_line(line) for
            line in molecule_block]

        # infers chemical formula from the molecule block
        molecule_block = np.array(molecule_block)
        atoms = molecule_block[:, 0]
        chemical_formula = Composition(''.join(atoms)).reduced_formula

        # parses scalar properties from the comments block
        comments_block_values = np.array([file_blocks.pop('comments')]).T
        properties = np.hstack([comments_block_values, COMMENTS_BLOCK_LABELS])
        properties = [dict(zip(['value', 'units', 'name'], row)) for row in
                      properties]

        # moves id_num and gdb9_string to a list of ids
        gdb = properties.pop(0)  # first list item is gdb9 string
        id_num = properties.pop(0)  # second list item is id number
        ids = []
        for item in [gdb, id_num]:
            item.pop('units')  # Ids do not have the units field
            ids.append(item)

        # appends vibrational frequencies to the property list
        vibrational_block = file_blocks.pop('vibrations')
        properties.append({'name': 'vibrational_frequencies', 'units': '1/cm',
                           'value': vibrational_block})

        # appends smiles and inchl to the ids list
        smiles_block = file_blocks.pop('smiles')
        ids.extend([{'name': 'smiles_gdb17', 'value': smiles_block[0]},
                    {'name': 'smiles_b3lyp', 'value': smiles_block[1]}])
        inchl_block = file_blocks.pop('inchl')
        ids.extend([{'name': 'inchl_corina', 'value': inchl_block[0]},
                    {'name': 'inchl_b3lyp', 'value': inchl_block[1]}])

        return cls(
            uid=uid, sub_systems=sub_systems, ids=ids,
            chemical_formula=chemical_formula, properties=properties,
            references=[{'doi': '10.1038/sdata.2014.22'}])

    @staticmethod
    def _parse_file_blocks(fh):
        """
        Parses an XMol XYZ file into blocks.

        Args:
            fh (TextIOBase) A file handle, usually obtained from open(file).

        Returns:
            (dict) Key-value mapping for the blocks in the file.
                n_atoms: int
                comments: list of str
                molecule: array-like
                vibrational_frequencies: list of float
                smiles: list of str
                inchl: list of str
        """

        n_atoms = int(fh.readline().strip())  # first line is n_atoms
        comments = fh.readline().strip().split()  # second line is comments

        molecule = []
        for i in range(n_atoms):  # next n_atom lines are element positions
            molecule.append(fh.readline().strip().split())

        vibrations = [  # next line is vibration frequencies
            float(i) for i in fh.readline().strip().split()]
        smiles = fh.readline().strip().split()  # next line is smiles strings
        inchl = fh.readline().strip().split()  # next line is InChl strings

        return {
            'n_atoms': n_atoms,
            'comments': comments,
            'molecule': molecule,
            'vibrations': vibrations,
            'smiles': smiles,
            'inchl': inchl
        }


if __name__ == '__main__':

    sys = XMolMolecularSystem.from_file('../data/dsgdb9nsd_133885.xyz')
    json = pif.dumps(sys)
    print(json)
