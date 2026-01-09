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
import argparse
from .__init__ import __version__, __package__
from .worker import work
from .util import (
    get_theme_path,
    load_config_file,
)


def main(argv=None):
    def parse_args(argv):
        parser = argparse.ArgumentParser(
            prog=__package__, description="convert markdown files into html"
        )
        parser.add_argument(
            "--input", "-i", help="path to input (notes) directory", required=True
        )
        parser.add_argument(
            "--output", "-o", help="path to output directory", required=True
        )
        parser.add_argument("--config", help="path to config.json", default="")
        parser.add_argument(
            "--clean",
            action="store_true",
            help="delete target location before creating files",
            default=False,
        )
        parser.add_argument(
            "--version", "-v", action="version", version=f"%(prog)s {__version__}"
        )
        return parser.parse_args(argv)

    args = parse_args(argv)

    # do error checking before touching any files
    infile = os.path.realpath(args.input)
    outfile = os.path.realpath(args.output)
    config_path = (
        os.path.realpath(args.config)
        if args.config
        else os.path.join(infile, "config.json")
    )
    if not os.path.exists(infile):
        print(f"{infile} not found")
        return 1

    config = load_config_file(config_path)

    for include_dir in config["general"]["include-dirs"]:
        included_dir = f"{infile}/{include_dir}"
        if not os.path.exists(included_dir):
            print(f"`include-dirs` contains `{included_dir}`, which does not exist")
            return 1
    theme_path = get_theme_path(config["general"]["theme"])
    if theme_path is None:
        print("Invalid theme name")
        return 1

    # finished error checking!
    # beyond here we always return 0

    expected_file = {
        "robots.txt": f"{infile}/robots.txt",
        "/img": f"{infile}/img",
        "/js": f"{infile}/js",
    }

    # DESTRUCTION (cleaning destination)
    if os.path.exists(outfile):
        if not args.clean:
            print("Target already exists. Re-run with --clean to overwrite")
            return 1
        shutil.rmtree(outfile)

    # CONSTRUCTION (copying directories)
    os.makedirs(outfile)
    # move theme
    shutil.copytree(theme_path, f"{outfile}/theme")
    shutil.move(f"{outfile}/theme/style.css", f"{outfile}/style.css")
    # move robots.txt
    if os.path.exists(expected_file["robots.txt"]):
        shutil.copy(expected_file["robots.txt"], f"{outfile}/robots.txt")
    else:
        print(
            f"\033[93mMissing `robots.txt` in {infile}; generating strict default\033[0m"
        )
        with open(f"{outfile}/robots.txt", "w") as fp:
            fp.writelines(["User-agent: *\n", "Disallow: /\n"])
    # optional directories
    if os.path.exists(expected_file["/img"]):
        shutil.copytree(expected_file["/img"], f"{outfile}/img")
    if os.path.exists(expected_file["/js"]):
        shutil.copytree(expected_file["/js"], f"{outfile}/js")
    for include_dir in config["general"]["include-dirs"]:
        shutil.copytree(f"{infile}/{include_dir}", f"{outfile}/{include_dir}")

    # Now convert the markdown files!
    work(config, infile, outfile)
    return 0
