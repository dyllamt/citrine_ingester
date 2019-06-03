import os
from shutil import copyfile

"""
Script for selecting a representative subset of the XMol dataset.
"""

destination_path = 'data_subset/'
source_path = '../../data/'
files = os.listdir(source_path)

# pick every 100 files
files = files[::100]
print(len(files))
for file in files:
    copyfile(source_path + file, destination_path + file)
