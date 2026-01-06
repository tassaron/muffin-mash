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

from mistune import create_markdown
from .util import get_route_name


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
    {'' if config['general']['logo'] is None else f'<img src="{config['general']['logo']}" style="{config['general']['logo-style']}" alt="{config['general']['logo-alt']}">'}
    <span id="header-title">{config['general']['title']}</span>
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
    nav_start = """<nav>"""
    nav_end = """</nav>"""
    get_route_name_ = lambda route: get_route_name(config, route).replace(" ", "&nbsp;")

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
                    f"<li><a href='/{encode_string(dirname)}/{'' if config['general']['pretty-urls'] else 'index.html'}'>{get_route_name_(dirname)}</a></li>"
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
