# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from pathlib import Path

import fire
from pymatgen import Structure, Lattice
from vise.input_set.datasets.potcar_set import PotcarSet
from vise.input_set.input_options import CategorizedInputOptions
from vise.input_set.task import Task
from vise.input_set.vasp_input_files import VaspInputFiles
from vise.input_set.xc import Xc


def make_atom_vasp_set(potcar_set: PotcarSet, xc: Xc):
    for element, potcar in potcar_set.potcar_dict().items():
        Path(element).mkdir()
        structure = Structure(Lattice.cubic(10),
                              coords=[[0.5]*3], species=[element])
        input_options = CategorizedInputOptions(structure,
                                                task=Task.cluster_opt,
                                                xc=xc,
                                                potcar_set=potcar_set)
        vasp_input_files = VaspInputFiles(
            input_options,
            overridden_incar_settings={"ISPIN": 2})
        vasp_input_files.create_input_files(dirname=Path(element))


if __name__ == '__main__':
    def make_set(_set, xc):
        make_atom_vasp_set(PotcarSet.from_string(_set), Xc.from_string(xc))

    fire.Fire(make_set)
