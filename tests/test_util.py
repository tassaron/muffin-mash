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

import pytest
from mash.util import *


@pytest.fixture
def toc():
    return {"test": []}


@pytest.fixture
def markdown():
    return find_markdown("notes")


@pytest.fixture
def config():
    return {**default_config}


def test_add_config_defaults(config, toc):
    toc["test"] = []
    add_folder_config_defaults(config, toc)
    assert config["folders"]["test"]["embeddable"] == False


def test_add_config_defaults_idempotent(config, toc):
    toc["test"] = []
    config["folders"]["test"] = {"embeddable": True}
    add_folder_config_defaults(config, toc)
    assert config["folders"]["test"]["embeddable"] == True


def test_find_markdown(markdown):
    assert markdown == [
        (
            "",
            "Example Page",
            ".md",
        ),
        (
            "",
            "config",
            ".json",
        ),
        (
            "",
            "index",
            ".md",
        ),
        (
            "",
            "robots",
            ".txt",
        ),
        (
            "Games",
            "Jezzball",
            ".html",
        ),
        (
            "Games",
            "index",
            ".md",
        ),
        (
            "Session Recaps",
            "Session 0",
            ".md",
        ),
        (
            "Session Recaps",
            "Session 1",
            ".md",
        ),
        (
            "Session Recaps",
            "Session 10",
            ".md",
        ),
        (
            "Session Recaps",
            "Session 11",
            ".md",
        ),
        (
            "Session Recaps",
            "Session 2",
            ".md",
        ),
        (
            "img",
            "muffin",
            ".svg",
        ),
        (
            "js",
            "jezzball-v1",
            ".js",
        ),
    ]


def test_create_tables_of_contents(config, markdown):
    assert create_tables_of_contents(config, markdown) == {
        "": ["Example Page"],
        "Session Recaps": [
            "Session 0",
            "Session 1",
            "Session 10",
            "Session 11",
            "Session 2",
        ],
        "Games": [
            "Jezzball",
        ],
    }
