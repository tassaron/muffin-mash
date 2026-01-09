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

import importlib
import json
import os

default_config = {
    "general": {
        "title": "Untitled",
        "theme": "default",
        "logo": None,
        "logo-alt": None,
        "logo-style": "width: 64px; height: 64px",
        "footer": "this is the footer text",
        "favicon": None,
        "pretty-urls": False,
        "route-names": {},
        "include-dirs": [],
    },
    "folders": {},
}


def get_route_name(config, route):
    if route in config["general"]["route-names"]:
        return config["general"]["route-names"][route]
    return route if "/" not in route else route.split("/", 1)[1]


def get_theme_path(theme_name: str):
    if theme_name == "default":
        theme_name = "brianna"
    try:
        theme_module = importlib.import_module(f"mash.themes.{theme_name}")
    except ImportError:
        return
    return theme_module.__path__[0]


def supported_ext(ext: str):
    return ext in [".md", ".html"]


def load_config_file(path):
    with open(path) as f:
        config = json.load(f)
    for key in default_config:
        if key not in config:
            config[key] = default_config[key]
    for key in default_config["general"]:
        if key not in config["general"]:
            config["general"][key] = default_config["general"][key]
    return config


def add_folder_config_defaults(config, toc):
    """idempotent function called immediately after discovering the folder structure to fix the config"""
    default_folder_config = {
        "sort-mode": "default",
        "sort-reverse": False,
        "embeddable": False,
        "nav-limit": -1,
    }
    for folder in toc:
        if folder not in config["folders"]:
            config["folders"][folder] = {}
        for key, default_val in default_folder_config.items():
            if key not in config["folders"][folder]:
                config["folders"][folder][key] = default_val


def create_tables_of_contents(config, working_files):
    working_files.sort()
    toc = {}
    for dir, filename, ext in working_files:
        if not supported_ext(ext) or dir.startswith("."):
            continue
        if dir not in toc:
            toc[dir] = []
        if filename == "index" and (
            dir == ""
            or dir not in config["folders"]
            or not config["folders"][dir].get("embeddable")
        ):
            continue
        toc[dir].append(filename)
    for key in toc:
        toc[key].sort()
    return toc


def find_markdown(infile):
    """Starting with a directory entrypoint, look for index.md and all other md files"""
    return sorted(
        [
            (
                os.path.basename(dir) if dir != infile else "",
                *os.path.splitext(filename),
            )
            for dir, _, files in os.walk(infile)
            for filename in files
        ]
    )


def sort_toc(config, toc):
    class SortFunction:
        """this is an ugly namespace I will change later"""

        @staticmethod
        def final_number(files):
            ordered_files = []
            for name in files:
                try:
                    num = int(name.split()[-1])
                except ValueError:
                    num = -1
                ordered_files.append((num, name))
            return [name for num, name in sorted(ordered_files)]

        @staticmethod
        def alphabetize(files):
            return sorted(files, key=lambda name: get_route_name(config, name).lower())

        @staticmethod
        def default(files):
            return files

    for folder in toc:
        toc[folder] = SortFunction.__dict__[config["folders"][folder]["sort-mode"]](
            toc[folder]
        )
        if config["folders"][folder]["sort-reverse"]:
            toc[folder].reverse()
    return toc
