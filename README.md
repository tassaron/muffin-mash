# muffin-mash

muffin-mash allows you to use **M**arkdown **A**s **S**tatic **H**TML. It is intentionally very simple, as it evolved from a simple script to **turn notes into a website**.

- only one level of folder depth is currently supported

## what does this do?

A notes folder structured like this:

```
index.md
Fruits/index.md
Fruits/Apple.md
Fruits/Orange.md
Veggies/index.md
Veggies/Kale.md
otherjunk/Muffins.md
```

Would generate a website with a sidebar like this:

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

Note: this requires a config file to make the contents of `otherjunk` "embeddable". This config option makes all files in the specified folder appear in the navigation instead of solely the index (and makes the index itself optional). See this [example `config.json` file](notes/config.json).

## how to install

- run `pipx install git+https://www.github.com/tassaron/muffin-mash` to install `mash` command
    - pipx is a friendly helper to install python packages in isolation (i.e. without affecting anything else on your system). If you are comfortable doing so, you can create a venv yourself and install with regular pip
- run `mash --help` for options

## how to use

**Example usage:** `mash --theme brianna --input $HOME/Documents/Notes --output /var/www/html`

### what should be in your notes

- a [`robots.txt`](https://en.wikipedia.org/wiki/Robots.txt) file
- contents of `js` and `img` will be blindly copied into output (so you can reliably import your js and images within notes)
- create `index.md` files in directories you want to be browsable
    - these files will have a **table of contents** appended
- table of contents for `index.md` in root directory will be used for site-wide navigation
- (optional) `config.json` in root directory

### note formatting language

You can mix markdown and HTML in your notes (you may need a blank line between HTML block elements and markdown content for proper detection).

The markdown syntax is ""standard"" except for this one modification:

- You can link locally between pages using `[[` and `]]`. You can also use a pipe character `|` to change the displayed link text.
    - [[example]] links to a page called "example" in the same folder and looks like "[example](https://example.com)"
    - [[test|example]] does the same, but the link text looks like "[test](https://example.com)"

### removing .html from final URLs

The `pretty-urls` general config option tells muffin-mash not to include .html at the end of links. This requires you to configure your webserver to server the files despite the lack of file extension. For example, see [this snippet from StackOverflow](https://stackoverflow.com/a/38238001) (copy-pasted below):

```nginx
location / {
    if ($request_uri ~ ^/(.*)\.html(\?|$)) {
        return 302 /$1;
    }
    try_files $uri $uri.html $uri/ =404;
}
```

## development

- run tests: `pip install pytest` and use `pytest` command

### todo

- nested folder support
- jinja templating would be nice
- better themes/theme integration (jinja would help with this)

## legal

- this program is [free software](/LICENSE)
- Atkinson fonts licensed under [OFL](https://openfontlicense.org/ofl-faq/)
