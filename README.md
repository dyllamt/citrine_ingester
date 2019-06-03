## Ingesting Data From QM9

QM9 is a computational quantum chemistry dataset of molecules. Each molecule is written to an XMol XYZ file that follows a block-like structure. A sublass of the pypif `ChemicalSystem` object represents each entry (`XMolMolecularSystem`), and there is a classmethod for generating this object from a file path. Documentation explains the system attributes and properties that are available for each entry. The molecular structure is made up of `XMolAtomicSystem` sub-systems, which have their own (documented) attributes and properties.

The dataset can be analyzed by loading the System entries into a `PifFrame`, which is a subclass of the pandas `DataFrame` object. One of the main advantages of the `PifFrame` is that is can be used to expose the sub-systems in a systems tree (*i.e.* each sub-system will get its own row instead of being imbeded in the row of its root system).

The `system_test.py` script demonstrates:
1. How each molecular system can be loaded from files
2. How `PifFrame` can be used to expose sub-systems
3. How to write these systems to the PIF schema

A subset of the QM9 dataset can be found in the **data** folder, and all code and stripts can be found in **src**.
