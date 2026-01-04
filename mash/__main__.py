"""
Copyright (C) 2025 Brianna Rainey
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
from pprint import pprint
from mistune import create_markdown
import importlib
import json


def get_theme_path(theme_name: str):
    try:
        theme_module = importlib.import_module(f"mash.themes.{theme_name}")
    except ImportError:
        return
    return theme_module.__path__[0]


def supported_ext(ext: str):
    return ext in [".md", ".html"]


def get_route_name(config, route):
    if route in config["general"]["route-names"]:
        return config["general"]["route-names"][route]
    return route if "/" not in route else route.split("/", 1)[1]


def create_page_converter(config, toc):
    convert_markdown_to_html = create_markdown(
        escape=False, renderer="html", plugins=["strikethrough"]
    )

    header = f"""<!doctype html><html>
    <head><title>{config['general']['title']}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
    <link rel="stylesheet" href="/style.css">
    {'' if config['general']['favicon'] is None else f'<link rel="icon" type="image/svg+xml" href="{config['general']['favicon']}">'}
    </head>
    <body>
    <div class="wrapper">
    
    <header>
    <a href="/{'' if config['general']['pretty-urls'] else 'index.html'}">
    {"" if config['general']['logo'] is None else f"<img src='{config["general"]["logo"]}' style='{config['general']['logo-style']}' alt='{config['general']['logo-alt']}'>"}
    {config['general']['title']}
    </a>
    </header>
    """

    footer = f"""<footer>{config["general"]["footer"]}<footer>
    </div>
    </body>
    </html>
    """
    content_start = """<article><div id='content'>"""
    content_end = """</div></article>"""
    nav_start = """<aside>"""
    nav_end = """</aside>"""
    get_route_name_ = lambda route: get_route_name(config, route)

    def encode_string(title):
        title = title.replace(" ", "%20")
        title = title.replace("'", "%27")
        return title

    def create_url(dir, title):
        sep = "/" if dir != "" else ""
        return f"/{encode_string(dir)}{sep}{'' if config['general']['pretty-urls'] and title=="index" else encode_string(title)}{'' if config["general"]["pretty-urls"] else '.html'}"

    def create_html_table_of_contents(dir, include_index=True):
        create_url_ = (
            lambda filename: f"<li><a href='{create_url(dir, filename)}'>{get_route_name_(f'{dir}/{filename}')}</a></li>"
        )
        li = []
        if include_index and "index" in toc[dir]:
            li.append(create_url_("index"))
        li.extend(
            [create_url_(filename) for filename in toc[dir] if filename != "index"]
        )
        return "".join(li)

    def add_links_to_folders(current_dir: str):
        li = []
        for dirname in toc.keys():
            if dirname == "":
                continue
            if config["folders"][dirname]["embeddable"]:
                li.append(create_html_table_of_contents(dirname))
            else:
                li.append(
                    f"<li><a href='/{encode_string(dirname)}/index.html'>{get_route_name_(dirname)}</a></li>"
                )
                if dirname == current_dir:
                    sub_toc = create_html_table_of_contents(dirname)
                    if sub_toc:
                        li.append(f"<li><ul>{sub_toc}</ul></li>")
        return "".join(li)

    def replace_local_links(dir, content):
        for linked_pair in range(min(content.count("[["), content.count("]]"))):
            start = content.index("[[")
            end = content[start + 1 :].index("]]") + start + 1
            label = content[start + 2 : end]
            if "|" in label:
                label, label_dest = label.split("|", 1)
            else:
                label_dest = label
            content = f"{content[:start]}[{label}]({create_url(dir, label_dest)}){content[end + 2:]}"
        return content

    def converter(filename, dir, ext, contents):
        h1 = (
            filename
            if f"{dir}/{filename}" not in config["general"]["route-names"]
            else config["general"]["route-names"][f"{dir}/{filename}"]
        )
        if not (dir == "" and filename == "index"):
            baseurl = f"{'' if dir == '' else '/'}{encode_string(dir)}"
            if config["folders"][dir]["embeddable"] or filename == "index":
                baseurl = ""
                if filename == "index":
                    h1 = (
                        dir
                        if dir not in config["general"]["route-names"]
                        else config["general"]["route-names"][dir]
                    )
            contents = (
                f"[< click to go back]({baseurl}/{'' if config['general']['pretty-urls'] else 'index.html'})\n# {h1}\n"
                + contents
            )
        contents = replace_local_links(dir, contents)
        contents = [
            header,
            nav_start,
            "<ul>",
            create_html_table_of_contents(""),
            add_links_to_folders(dir),
            "</ul>",
            nav_end,
            content_start,
            convert_markdown_to_html(contents),
            f"{'' if dir=='' or filename != 'index' else create_html_table_of_contents(dir, include_index=False)}",
        ]

        return "".join([*contents, content_end, footer])

    return converter


def load_config_file(path=None):
    default_config = {
        "general": {
            "title": "Untitled",
            "theme": "default",
            "logo": None,
            "logo-alt": None,
            "logo-style": "width: 64px; height: 64px",
            "footer": "this is the footer text",
            "favicon": None,
            "route-names": {},
            "pretty-urls": False,
        },
        "folders": {},
    }
    if path is None:
        return default_config
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
        "embeddable": False,
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
            or not config["folders"][dir]["embeddable"]
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
    return toc


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


def main(argv=None):
    def parse_args(argv):
        parser = argparse.ArgumentParser(description="convert markdown files into html")
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
        return parser.parse_args(argv)

    args = parse_args(argv)

    # use parsed args
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
    if os.path.exists(outfile):
        if not args.clean:
            print("Target already exists. Re-run with --clean to overwrite")
            return 1
        shutil.rmtree(outfile)
    theme_path = get_theme_path(config["general"]["theme"])
    if theme_path is None:
        print("Invalid theme name")
        return 1
    shutil.copytree(theme_path, outfile)
    shutil.copy(f"{infile}/robots.txt", f"{outfile}/robots.txt")
    shutil.copytree(f"{infile}/img", f"{outfile}/img")
    shutil.copytree(f"{infile}/js", f"{outfile}/js")
    work(config, infile, outfile)
    return 0
