# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

from argparse import Namespace
from pathlib import Path

from pydefect.cli.vasp.make_defect_charge_info import make_spin_charges
from pymatgen.io.vasp import Chgcar
from vise.analyzer.vasp.handle_volumetric_data import \
    light_weight_vol_text
from vise.analyzer.vesta.vesta_file import add_density, VestaFile, calc_isurfs
from vise.atom_energies.make_atom_vasp_set import make_atom_poscar_dirs
from vise.util.logger import get_logger

logger = get_logger(__name__)


def make_atom_poscars(args: Namespace) -> None:
    make_atom_poscar_dirs(args.dirname, args.elements)


def make_spin_decomposed_volumetric_files(args):
    chgcar = Chgcar.from_file(args.chgcar)
    for c, spin in zip(make_spin_charges(chgcar), ["up", "down"]):
        c.write_file(f"{args.chgcar}_{spin}")


def make_light_weight_vol_data(args):
    chgcar = Chgcar.from_file(args.volumetric_file)
    output_vol_filename = (args.output_lw_volumetric_filename
                           or Path(f"{args.volumetric_file}_lw"))
    lw_vol_text = light_weight_vol_text(chgcar, args.border_fractions)
    Path(output_vol_filename).write_text(lw_vol_text)

    if args.output_vesta_filename:
        is_chg = "CHG" in args.volumetric_file
        volume = chgcar.structure.volume
        isurfs = calc_isurfs(args.border_fractions, is_chg, volume)

        if args.original_vesta_file:
            vesta_text = args.original_vesta_file.read_text()
        else:
            vesta_text = VestaFile(chgcar.structure).__repr__()
        to_vesta_text = add_density(vesta_text, isurfs, str(output_vol_filename))
        Path(args.output_vesta_filename).write_text(to_vesta_text)