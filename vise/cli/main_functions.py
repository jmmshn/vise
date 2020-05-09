# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

from argparse import Namespace
from pathlib import Path
from copy import deepcopy

from pymatgen.ext.matproj import MPRester
from pymatgen import Structure

from vise.input_set.input_options import CategorizedInputOptions, assignable_option_set
from vise.input_set.vasp_input_files import VaspInputFiles
from vise.defaults import defaults
from vise.input_set.prior_info import PriorInfoFromCalcDir
from vise.input_set.kpoints_mode import KpointsMode
from vise.cli.main_tools import potcar_str2dict, list2dict

from vise.analyzer.vasp.plot_band import VaspBandPlotInfo
from vise.analyzer.plot_band import BandPlotter

from vise.analyzer.vasp.dos_data import VaspDosData
from vise.analyzer.plot_dos import DosPlotter
from vise.analyzer.vasp.band_edge_properties import VaspBandEdgeProperties
from pymatgen.io.vasp import Vasprun, Outcar


def get_poscar_from_mp(args: Namespace) -> None:
    s = MPRester().get_structure_by_material_id(args.mpid)
    s.to(fmt="poscar", filename=args.poscar)


class VaspSet:
    def __init__(self, args: Namespace):
        self.args = args
        self._file_transfers = None

        options = CategorizedInputOptions(
            structure=self._structure(),
            task=args.task,
            xc=args.xc,
            kpt_density=args.kpt_density,
            overridden_potcar=self._overridden_potcar(),
            charge=args.charge,
            **self._option_kwargs())

        vif = VaspInputFiles(options, self._overridden_incar_settings())
        vif.create_input_files(Path.cwd())
        if self._file_transfers:
            self._file_transfers.transfer()

    def _structure(self):
        return Structure.from_file(self.args.poscar)

    def _overridden_incar_settings(self):
        result = deepcopy(defaults.user_incar_settings)
        if self.args.user_incar_settings:
            result.update(self.args.user_incar_settings)

        return result

    def _overridden_potcar(self):
        result = deepcopy(defaults.overridden_potcar)
        if self.args.overridden_potcar:
            result.update(potcar_str2dict(self.args.overridden_potcar))
        return result

    def _option_kwargs(self):
        result = deepcopy(defaults.options)
        if self.args.prev_dir:
            pi = PriorInfoFromCalcDir(self.args.prev_dir,
                                      self.args.file_transfer_type)
            result.update(pi.input_options_kwargs)
            self._file_transfers = pi.file_transfers

        if self.args.options:
            args = list2dict(self.args.options, assignable_option_set)
            result.update(args)
        if self.args.uniform_kpt_mode:
            result["kpt_mode"] = KpointsMode.uniform

        return result


def plot_band(args: Namespace):
    plot_info = VaspBandPlotInfo(vasprun=Vasprun(args.vasprun_filepath),
                                 kpoints_filename=args.kpoints_filename)
    plotter = BandPlotter(plot_info, y_range=args.y_range)
    plotter.construct_plot()
    plotter.plt.savefig(args.filename, format="pdf")


def plot_dos(args: Namespace):
    vasprun = Vasprun(args.vasprun)
    outcar = Outcar(args.outcar)
    band_edge = VaspBandEdgeProperties(vasprun, outcar)
    if band_edge.band_gap:
        vertical_lines = [band_edge.vbm_info.energy, band_edge.cbm_info.energy]
    else:
        vertical_lines = [vasprun.efermi]

    dos_data = VaspDosData(vasprun)
    structure = vasprun.final_structure
    grouped_atom_indices = args.type.grouped_atom_indices(structure, args.target)
    plot_data = dos_data.dos_plot_data(grouped_atom_indices,
                                       vertical_lines=vertical_lines,
                                       xlim=args.x_range)
#                                       ylim_set=args.y_range)
    plotter = DosPlotter(plot_data, args.legend)
    plotter.construct_plot()
    plotter.plt.show()


