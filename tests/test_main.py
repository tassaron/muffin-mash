"""
Copyright (C) 2026 Brianna Rainey
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import tempfile
import shutil
import json
import pytest
from mash.__main__ import main


def tmp():
    tmp_path = tempfile.mkdtemp()
    try:
        yield tmp_path
    finally:
        shutil.rmtree(tmp_path)


tmp1 = pytest.fixture(tmp)
tmp2 = pytest.fixture(tmp)


def test_main_creates_index(tmp1):
    old_dir_state = os.path.exists(f"{tmp1}/index.html")
    main(["-i", "notes", "-o", tmp1, "--clean"])
    assert os.path.exists(f"{tmp1}/index.html") != old_dir_state


def test_main_include_dirs_fail(tmp1, tmp2):
    shutil.copytree("notes", f"{tmp1}/notes")
    with open(f"{tmp1}/notes/config.json", "r") as fp:
        this_config = json.load(fp)
    this_config["general"]["include-dirs"] = ["test"]
    with open(f"{tmp1}/notes/config.json", "w") as fp:
        json.dump(this_config, fp)
    returnval = main(
        ["-i", f"{tmp1}/notes", "-o", tmp2, "--clean"],
    )
    assert returnval == 1


def test_main_config_include_dirs_succeed(tmp1, tmp2):
    shutil.copytree("notes", f"{tmp1}/notes")
    with open(f"{tmp1}/notes/config.json", "r") as fp:
        this_config = json.load(fp)
    this_config["general"]["include-dirs"] = ["test"]
    with open(f"{tmp1}/notes/config.json", "w") as fp:
        json.dump(this_config, fp)
    os.makedirs(f"{tmp1}/notes/test")
    returnval = main(
        ["-i", f"{tmp1}/notes", "-o", tmp2, "--clean"],
    )
    assert returnval == 0


def test_main_config_include_dirs_copies_file(tmp1, tmp2):
    shutil.copytree("notes", f"{tmp1}/notes")
    with open(f"{tmp1}/notes/config.json", "r") as fp:
        this_config = json.load(fp)
    this_config["general"]["include-dirs"] = ["test"]
    with open(f"{tmp1}/notes/config.json", "w") as fp:
        json.dump(this_config, fp)
    os.makedirs(f"{tmp1}/notes/test")
    with open(f"{tmp1}/notes/test/not-markdown.txt", "w") as fp:
        fp.write("example")
    main(
        ["-i", f"{tmp1}/notes", "-o", tmp2, "--clean"],
    )
    with open(f"{tmp1}/notes/test/not-markdown.txt", "r") as fp:
        content = fp.readlines()
    assert content == ["example"]
