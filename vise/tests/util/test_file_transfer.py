# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

import os
from pathlib import Path
import tempfile

import pytest

from vise.util.file_transfer import (
    FileTransfer, FileMove, FileCopy, FileLink, FileTransfers)


cwd = Path.cwd().absolute()


@pytest.fixture()
def file_transfer_instance():
    class Test(FileTransfer):
        def transfer(self, abs_output_dir):
            pass

    return Test(abs_file_path=cwd / "a")


def test_file_transfer_abs_file_path(file_transfer_instance):
    assert file_transfer_instance.abs_in_file == cwd / "a"


def test_file_transfer_file_name(file_transfer_instance):
    assert file_transfer_instance.file_name == "a"


def test_file_transfer_to(file_transfer_instance):
    assert file_transfer_instance.to(Path("b")) == cwd / "b" / "a"


def test_file_move():
    print_string = "test"
    filename = "a"
    with tempfile.TemporaryDirectory() as tmp_from:
        file_move = FileMove(abs_file_path=Path(tmp_from) / filename)
        os.chdir(tmp_from)

        with open(filename, "w") as f1:
            print(print_string, end="", file=f1)

        with tempfile.TemporaryDirectory() as tmp_to:
            file_move.transfer(Path(tmp_to))
            os.chdir(Path(tmp_to))

            with open(Path(tmp_to) / filename, 'r') as f2:
                assert f2.read() == print_string


def test_file_copy():
    print_string = "test"
    filename = "a"
    with tempfile.TemporaryDirectory() as tmp_from:
        file_copy = FileCopy(abs_file_path=Path(tmp_from) / filename)
        os.chdir(tmp_from)

        with open(filename, "w") as f1:
            print(print_string, end="", file=f1)

        with tempfile.TemporaryDirectory() as tmp_to:
            file_copy.transfer(Path(tmp_to))
            os.chdir(Path(tmp_to))

            with open(Path(tmp_to) / filename, 'r') as f_to:
                with open(Path(tmp_from) / filename, 'r') as f_from:
                    assert f_to.read() == f_from.read()


def test_file_link():
    print_string = "test"
    filename = "a"
    with tempfile.TemporaryDirectory() as tmp_from:
        file_link = FileLink(abs_file_path=Path(tmp_from) / filename)
        os.chdir(tmp_from)

        with open(filename, "w") as f1:
            print(print_string, end="", file=f1)

        with tempfile.TemporaryDirectory() as tmp_to:
            file_link.transfer(Path(tmp_to))

            assert (Path(tmp_to) / filename).is_symlink()

            os.chdir(Path(tmp_to))

            with open(Path(tmp_to) / filename, 'r') as f_to:
                with open(Path(tmp_from) / filename, 'r') as f_from:
                    assert f_to.read() == f_from.read()


def test_transfer_files():
    test_string = "test"
    with tempfile.TemporaryDirectory() as tmp_from:
        os.chdir(tmp_from)
        for i in ["file1", "file2", "file3", "file4"]:
            with open(i, "w") as f1:
                print(test_string, end="", file=f1)
        file_transfers = FileTransfers.from_dict(
            {"file1": "m", "file2": "c", "file3": "l", "file4": "m"},
            path=Path(tmp_from))

        with tempfile.TemporaryDirectory() as tmp_to:
            file_transfers.transfer(Path(tmp_to))
            for i in ["file2", "file3"]:
                with open(Path(tmp_to) / i, 'r') as f_to:
                    with open(Path(tmp_from) / i, 'r') as f_from:
                        assert f_to.read() == f_from.read()
            for i in ["file1", "file4"]:
                with open(Path(tmp_to) / i, 'r') as f2:
                    assert f2.read() == test_string


def test_transfer_files_logger_non_exist(mocker):
    mock = mocker.patch("vise.util.file_transfer.logger.warning")
    non_exist_filename = "a"

    with tempfile.TemporaryDirectory() as tmp_from:
        os.chdir(tmp_from)
        FileTransfers.from_dict({non_exist_filename: "m"}, path=Path(tmp_from))
        mock.assert_called_once_with(
            f"{Path(tmp_from) / non_exist_filename} does not exist.")


def test_transfer_files_logger_empty(mocker):
    mock = mocker.patch("vise.util.file_transfer.logger.warning")
    empty_filename = "b"

    with tempfile.TemporaryDirectory() as tmp_from:
        os.chdir(tmp_from)
        with open(empty_filename, "w") as f1:
            print("", end="", file=f1)
        FileTransfers.from_dict({empty_filename: "m"}, path=Path(tmp_from))
        mock.assert_called_once_with(
            f"{Path(tmp_from) / empty_filename} is empty.")


def test_transfer_files_logger_warning(mocker):
    mock = mocker.patch("vise.util.file_transfer.logger.warning")
    filename = "c"
    print_string = "test"

    with tempfile.TemporaryDirectory() as tmp_from:
        os.chdir(tmp_from)
        with open(filename, "w") as f2:
            print(print_string, end="", file=f2)
        FileTransfers.from_dict({filename: "x"}, path=Path(tmp_from))
        mock.assert_called_once_with(
            f"x option for {filename} is invalid.")


def test_transfer_delete():
    with tempfile.TemporaryDirectory() as tmp_from:
        os.chdir(tmp_from)
        for i in ["a", "bbb", "cbb", "bd", "bda"]:
            with open(i, "w") as f1:
                print("test", end="", file=f1)
        file_transfers = FileTransfers.from_dict({"a":   "m",
                                                  "bbb": "c",
                                                  "cbb": "l",
                                                  "bd":  "m",
                                                  "bda": "m"},
                                                 path=Path(tmp_from))
        file_transfers.delete_file_transfers_w_keywords(["bb", "a"])
        assert len(file_transfers.file_transfer_list) == 1