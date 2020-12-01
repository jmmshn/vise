# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from math import log10
from typing import List

from matplotlib import pyplot as plt
from plotly import graph_objects as go
from vise.analyzer.dielectric_function import DieleFuncData
from vise.analyzer.dielectric_function_data.exp_dielectric_func import \
    ExpDieleFunc
from vise.util.matplotlib import float_to_int_formatter


class AbsorptionCoeffPlotter:

    def __init__(self,
                 diele_func_data: DieleFuncData,
                 energy_range: List[float] = None,
                 coeff_power_range: List[float] = None,
                 materials: List[str] = None):

        self.energies = diele_func_data.energies
        self.absorption_coeff = diele_func_data.ave_absorption_coeff
        self.band_gap = diele_func_data.band_gap
        self.energy_range = energy_range or [0, 10]
        self.coeff_power_range = coeff_power_range
        self.materials = materials

        self.xaxis_title = "Energy (eV)"
        self.yaxis_title = "Absorption coefficient. (cm-1)"
        self.ymin = 10**3
        self.ymax = 10**7

        self.plt = plt


class AbsorptionCoeffPlotlyPlotter(AbsorptionCoeffPlotter):
    def create_figure(self):
        fig = go.Figure()
        fig.update_layout(
            xaxis_title=self.xaxis_title,
            yaxis_title=self.yaxis_title,
            font_size=15,
            width=800, height=700)

        fig.add_trace(go.Scatter(x=self.energies,
                                 y=self.absorption_coeff,
                                 name="calc"))
        fig.add_trace(go.Scatter(x=[self.band_gap, self.band_gap],
                                 y=[self.ymin, self.ymax],
                                 line=dict(width=1, dash="dash"),
                                 showlegend=False,
                                 line_color="black",
                                 name="calculated band gap"))

        if self.materials:
            for material in self.materials:
                exp = ExpDieleFunc(material)
                energies = exp.energies
                fig.add_trace(go.Scatter(x=[exp.band_gap, exp.band_gap],
                                         y=[self.ymin, self.ymax],
                                         line=dict(width=1, dash="dash"),
                                         showlegend=False,
                                         line_color="black",
                                         name=f"{material} band gap"))

                fig.add_trace(go.Scatter(x=energies, y=exp.absorption_coeff,
                                         line=dict(width=1, dash="dashdot"),
                                         name=material))

        fig["layout"]["xaxis"]["range"] = self.energy_range
        fig["layout"]["yaxis"]["range"] = [log10(self.ymin), log10(self.ymax)]
        fig.update_yaxes(type="log")
        return fig


class AbsorptionCoeffMplPlotter(AbsorptionCoeffPlotter):

    def construct_plot(self, add_directions: bool = True):
        self._add_coeffs()
        self._add_band_gap()
        if self.materials:
            self._add_materials()
        self._set_figure_legend()
        self._set_x_range()
        self._set_y_range()
        self._set_labels()
        self._set_formatter()
        self.plt.tight_layout()

    def _add_coeffs(self):
        self.plt.semilogy(self.energies, self.absorption_coeff)

    def _add_band_gap(self):
        self.plt.axvline(x=self.band_gap, linestyle="dashed", color="black",
                         linewidth=1)

    def _add_materials(self):
        for material in self.materials:
            exp = ExpDieleFunc(material)
            energies = exp.energies
            self.plt.axvline(x=exp.band_gap,
                             linestyle="dashed",
                             color="black",
                             linewidth=1)

            self.plt.semilogy(energies,
                              list(exp.absorption_coeff),
                              label=material,
                              linestyle="dashdot",
                              )

    def _set_figure_legend(self):
        self.plt.legend(loc="lower right")

    def _set_x_range(self):
        self.plt.xlim(0, 10)

    def _set_y_range(self):
        self.plt.gca().set_ylim(ymin=self.ymin, ymax=self.ymax)

    def _set_labels(self):
        self.plt.xlabel(self.xaxis_title)
        self.plt.ylabel(self.yaxis_title)

    def _set_formatter(self):
        axis = self.plt.gca()
        axis.xaxis.set_major_formatter(float_to_int_formatter)