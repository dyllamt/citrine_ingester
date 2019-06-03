import sys
sys.path.append('./base/')

from glob import glob
from pifframe import PifFrame
from pypif import pif
from xmolsystem import XMolMolecularSystem

"""
Script testing the extraction of molecular systems from XYZ files.
"""


def test_frame_to_pif(frame, file='./test.json', nest_sub_systems=False):
    """
    Save a PIF file from a pandas DataFrame.

    Args:
        frame (PifFrame) DataFrame containing System entries.
        file (str) File name to write to.
    """
    systems = frame.to_pif_systems(nest_sub_systems=nest_sub_systems)
    with open(file, 'w') as fp:
        pif.dump(systems, fp, indent=4)


if __name__ == '__main__':

    # gets the file names in the dataset
    files = glob('../data/data_subset/*.xyz')

    # loads each file as a chemical system
    systems = [XMolMolecularSystem.from_file(file) for file in files]

    # loads the systems into a dataframe for analysis
    frame = PifFrame.from_pif_systems(systems)
    print(frame[['chemicalFormula', 'uid']])  # sub-systems are exposed

    # writes the dataframe to a pif file (for speed, don't expose sub-systems)
    frame = PifFrame.from_pif_systems(systems, expose_sub_systems=False)
    test_frame_to_pif(frame)
    print('done writing!')
