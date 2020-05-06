# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

from copy import deepcopy
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt
from pymatgen import Spin
from vise.util.matplotlib import float_to_int_formatter
from num2words import num2words


@dataclass(frozen=True)
class XTicks:
    labels: List[str]
    distances: List[float]


@dataclass
class BandEdge:
    vbm: float
    cbm: float
    vbm_distances: List[float]
    cbm_distances: List[float]


class BandInfo:
    def __init__(self,
                 band_energies: List[List[List[List[float]]]],
                 band_edge: Optional[BandEdge] = None,
                 fermi_level: Optional[float] = None):
        self.band_energies = deepcopy(band_energies)
        self.band_edge = deepcopy(band_edge)
        self.fermi_level = fermi_level

        if self.band_edge is None and self.fermi_level is None:
            raise ViseBandInfoError

    def slide_energies(self, reference_energy):
        self._slide_band_energies(reference_energy)
        self._slide_band_edge(reference_energy)
        self._slide_fermi_level(reference_energy)

    def _slide_band_energies(self, reference_energy):
        new_array = []
        for band_energies_each_branch in self.band_energies:
            a = np.array(band_energies_each_branch)
            new_array.append((a - reference_energy).tolist())

    def _slide_fermi_level(self, reference_energy):
        if self.fermi_level:
            self.fermi_level -= reference_energy

    def _slide_band_edge(self, reference_energy):
        if self.band_edge:
            self.band_edge.vbm -= reference_energy
            self.band_edge.cbm -= reference_energy

    @property
    def is_magnetic(self):
        return len(self.band_energies[0]) == 2


class ViseBandInfoError(Exception):
    pass


class BandMplDefaults:
    def __init__(self,
                 colors: Optional[List[str]] = None,
                 linewidth: float = 1.0,
                 circle_size: int = 70,
                 circle_colors: Optional[List[str]] = None,
                 band_edge_line_width: float = 0.75,
                 band_edge_line_color: str = "black",
                 band_edge_line_style: str = "-.",
                 title_font_size: int = 15,
                 label_font_size: int = 15,
                 legend_location: str = "lower right"
                 ):
        self.colors = colors or ['#E15759', '#4E79A7', '#F28E2B', '#76B7B2']
        self.linewidth = linewidth

        self.circle_size = circle_size
        self.hline = {"linewidth": band_edge_line_width,
                      "color": band_edge_line_color,
                      "linestyle": band_edge_line_style}

        self.title_font_size = title_font_size
        self.label_font_size = label_font_size

        self.circle_colors = circle_colors or ["pink", "green"]
        self.circle_size = circle_size

        self.legend = {"loc": legend_location}

    def band_structure(self, index):
        return {"color": self.colors[index],
                "linewidth": self.linewidth,
                "label": num2words(index + 1, ordinal=True)}

    def circle(self, index):
        return {"color": self.colors[index],
                "marker": "o",
                "s": self.circle_size}


class BandPlotter:

    def __init__(self,
                 band_info_set: List[BandInfo],
                 distances_by_branch: List[List[float]],
                 x_ticks: XTicks,
                 y_range: List[float],
                 title: str = None,
                 reference_energy: float = None,
                 mpl_defaults: Optional[BandMplDefaults] = BandMplDefaults()
                 ):

        assert distances_by_branch[0][0] == x_ticks.distances[0]
        assert distances_by_branch[-1][-1] == x_ticks.distances[-1]

        self.band_info_set = band_info_set
        self.distances_by_branch = distances_by_branch
        self.x_ticks = x_ticks
        self.y_range = y_range
        self.title = title
        self.mpl_defaults = mpl_defaults
        self.plt = plt

        self._slide_energies(reference_energy)

    def _slide_energies(self, reference_energy):
        if reference_energy is None:
            if self.band_info_set[0].band_edge is not None:
                reference_energy = self.band_info_set[0].band_edge.vbm
            elif self.band_info_set[0].fermi_level:
                reference_energy = self.band_info_set[0].fermi_level

        self.band_info_set[0].slide_energies(reference_energy)

    def construct_plot(self):
        self._add_band_set()
        self._set_figure_legend()
        self._set_x_range()
        self._set_y_range()
        self._set_labels()
        self._set_x_ticks()
        self._set_title()
        self._set_formatter()
        self.plt.tight_layout()

    def _add_band_set(self):
        for index, band_info in enumerate(self.band_info_set):
            self._add_band_structures(band_info, index)

            if band_info.band_edge:
                self._add_band_edge(band_info.band_edge, index)

            if band_info.fermi_level:
                self._add_fermi_level(band_info.fermi_level)

    def _add_band_structures(self, band_info, index):
        mpl_args = self.mpl_defaults.band_structure(index)
        for distances, energies_each_branch \
                in zip(self.distances_by_branch,  band_info.band_energies):
            for i, energies_of_each_spin in enumerate(energies_each_branch):
                self._set_linestyle(i, mpl_args)
                for energies_of_a_band in energies_of_each_spin:
                    self.plt.plot(distances, energies_of_a_band, **mpl_args)
                    mpl_args.pop("label", None)

    @staticmethod
    def _set_linestyle(i, mpl_args):
        if i == 0:
            mpl_args.pop("linestyle", None)
        else:
            mpl_args["linestyle"] = ":"

    def _add_band_edge(self, band_edge, index):
        self.plt.axhline(y=band_edge.vbm, **self.mpl_defaults.hline)
        self.plt.axhline(y=band_edge.cbm, **self.mpl_defaults.hline)

        for dist in band_edge.vbm_distances:
            self.plt.scatter(dist, band_edge.vbm,
                             **self.mpl_defaults.circle(index))
        for dist in band_edge.cbm_distances:
            self.plt.scatter(dist, band_edge.cbm,
                             **self.mpl_defaults.circle(index))

    def _add_fermi_level(self, fermi_level):
        self.plt.axhline(y=fermi_level, **self.mpl_defaults.hline)

    def _set_figure_legend(self):
        self.plt.legend(**self.mpl_defaults.legend)

    def _set_x_range(self):
        self.plt.xlim(self.x_ticks.distances[0], self.x_ticks.distances[-1])

    def _set_y_range(self):
        self.plt.ylim(self.y_range[0], self.y_range[1])

    def _set_labels(self):
        self.plt.xlabel("Wave vector", size=self.mpl_defaults.label_font_size)
        self.plt.ylabel("Energy (eV)", size=self.mpl_defaults.label_font_size)

    def _set_x_ticks(self):
        axis = self.plt.gca()
        axis.set_xticks(self.x_ticks.distances)
        axis.set_xticklabels(self.x_ticks.labels)
        for distance, label in zip(self.x_ticks.distances[1:-1],
                                   self.x_ticks.labels[1:-1]):
            linestyle = "-" if "\\mid" in label else "--"
            plt.axvline(x=distance, linestyle=linestyle)

    def _set_title(self):
        self.plt.title(self.title, size=self.mpl_defaults.title_font_size)

    def _set_formatter(self):
        axis = self.plt.gca()
        axis.yaxis.set_major_formatter(float_to_int_formatter)


