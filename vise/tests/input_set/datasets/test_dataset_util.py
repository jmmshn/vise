# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

import pytest

from pymatgen import Composition
from pymatgen.io.vasp import Potcar

from vise.input_set.datasets.dataset_util import (
    LDAU, PotcarSet, unoccupied_bands, num_bands, npar_kpar)


def test_ldau_3d_transition_metal():
    actual = LDAU(symbol_list=["Mn", "Cu"], )
    assert actual.ldauu == [3, 5]
    assert actual.ldaul == [2, 2]
    assert actual.lmaxmix == 4


def test_ldau_rare_earth():
    actual = LDAU(symbol_list=["Mn", "Ho"], )
    assert actual.ldauu == [3, 5]
    assert actual.ldaul == [2, 3]
    assert actual.lmaxmix == 6


def test_ldau_3d_override():
    actual = LDAU(symbol_list=["Mn", "Cu"],
                  override_ldauu={"Mn": 10}, override_ldaul={"Cu": 100})
    assert actual.ldauu == [10, 5]
    assert actual.ldaul == [2, 100]
    assert actual.lmaxmix == 4


def test_potcar_list_normal():
    potcar_list = PotcarSet.normal.potcar_list()
    assert potcar_list["H"] == "H"


def test_potcar_list_gw():
    potcar_list = PotcarSet.gw.potcar_list()
    assert potcar_list["Li"] == "Li_GW"


def test_potcar_list_non():
    potcar_list = PotcarSet.mp_relax_set.potcar_list()
    assert potcar_list["Fr"] is None
    assert potcar_list["Sr"] == "Sr_sv"


def test_potcar_set():
    assert PotcarSet.normal.potcar_dict()["Li"] == "Li"


def test_potcar_set_override():
    actual = PotcarSet.normal.potcar_dict({"Li": "Li_test"})["Li"]
    assert actual == "Li_test"


def test_unoccupied_bands():
    assert unoccupied_bands["H"] == 4


def test_nbands():
    composition = Composition("KH2")
    potcar = Potcar(symbols=["K_pv", "H"], functional="PBE")
    # Nelect of K_pv is 7, so (7 + 1 * 2) / 2 + (9 + 4 * 2) = 22
    assert num_bands(composition, potcar) == 22


def test_npar_kpar():
    assert npar_kpar(num_kpoints=10, num_nodes=5) == (2, 1)
    assert npar_kpar(num_kpoints=100, num_nodes=4) == (16, 1)
