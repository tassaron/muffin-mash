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
import shutil
from pprint import pprint
from .converter import create_page_converter
from .util import (
    find_markdown,
    create_tables_of_contents,
    add_folder_config_defaults,
    sort_toc,
    supported_ext,
)


def work(config, infile, outfile):
    working_files = find_markdown(infile)
    toc = create_tables_of_contents(config, working_files)
    add_folder_config_defaults(config, toc)
    toc = sort_toc(config, toc)
    print("\033[92mmuffin-mash created this table of contents:\033[0m")
    pprint(toc, indent=4)

    # create HTML files!!
    convert_markdown_to_html = create_page_converter(config, toc)
    for dir, filename, ext in working_files:
        if not supported_ext(ext):
            continue

        # create output directory
        outdir = os.path.join(outfile, dir)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        if ext == "html":
            shutil.copy(
                f"{os.path.join(infile, dir, filename)}{ext}",
                f"{os.path.join(outdir, filename)}.html",
            )
            continue

        # read markdown into a string
        with open(f"{os.path.join(infile, dir, filename)}{ext}", "r") as f:
            contents = "".join(f.readlines())

        # convert markdown to html
        this_html = convert_markdown_to_html(filename, dir, ext, contents)

        # create html file
        with open(f"{os.path.join(outdir, filename)}.html", "w") as f:
            f.write(this_html)
