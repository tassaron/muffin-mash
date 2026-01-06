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
from mash.converter import create_page_converter
from mash.util import default_config, create_tables_of_contents


@pytest.fixture
def converter():
    yield create_page_converter(
        default_config,
        create_tables_of_contents(default_config, [("", "index", ".md")]),
    )


def test_converter_adds_page_title(converter):
    title = default_config["general"]["title"]
    converted = converter("index", "", ".md", "")
    gayi = converted.index(title)
    assert (
        converted[gayi - 7 : gayi + len(title) + 8]
        == f"<title>{default_config["general"]["title"]}</title>"
    )
