# muffin-mash

muffin-mash allows you to use **M**arkdown **A**s **S**tatic **H**TML. It is intentionally very simple, as it evolved from a simple script to **turn notes into a website**.

## how to use

- run `pipx install git+https://www.github.com/tassaron/muffin-mash` to install `mash` command
    - pipx is a friendly helper to install python packages in isolation (i.e. without affecting anything else on your system). If you are comfortable doing so, you can create a venv yourself and install with regular pip
- run `mash --help` for options

**Example usage:** `mash --theme brianna --input $HOME/Documents/Notes --output /var/www/html`

### what should be in your notes

- a [`robots.txt`](https://en.wikipedia.org/wiki/Robots.txt) file
- contents of `js` and `img` will be blindly copied into output (so you can reliably import your js and images within notes)
- create `index.md` files in directories you want to be browsable
    - these files will have a **table of contents** appended
- table of contents for `index.md` in root directory will be used for site-wide navigation
- (optional) `config.json` in each directory telling muffin-mash special stuff about that directory (e.g., sorting mode)

#### Example

A notes folder structured such as this:

```
index.md
Fruits/index.md
Fruits/Apple.md
Fruits/Orange.md
Veggies/index.md
Veggies/Kale.md
otherjunk/Muffins.md
```

Would have a website with a sidebar reading:

```
Fruits
Veggies
Muffins
```

The homepage of this site displays the actual content of `index.md`, and each navigation link to a folder leads to its own `index.md`. When `Fruits` is selected, the navigation bar will look like this:

```
Fruits
 • Apple
 • Orange
Veggies
Muffins
```

Note: this requires a config file to make the contents of `otherjunk` embeddable.

### known quirks

- the urls are ugly as hell, since filenames are used as page titles. will fix this soon
- folders cannot only have an index without other pages
- script doesn't track which folders have an index and which don't, thus folders will be assumed to have an index if they aren't embeddable
- nested folders are currently unsupported

## development

- run tests: `pip install pytest` and use `pytest` command

### todo

- config documentation
- nested folder support
- jinja templating would be nice
- better themes/theme integration (jinja would help with this)

## legal

- this program is [free software](/LICENSE)
- Atkinson fonts licensed under [OFL](https://openfontlicense.org/ofl-faq/)
