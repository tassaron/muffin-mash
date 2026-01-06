import os
import shutil
import tempfile
import pytest
from mash.__main__ import *


@pytest.fixture
def toc():
    return {"test": []}


@pytest.fixture
def markdown():
    return find_markdown("notes")


@pytest.fixture
def config():
    return load_config_file()


def tmp():
    tmp_path = tempfile.mkdtemp()
    try:
        yield tmp_path
    finally:
        shutil.rmtree(tmp_path)


tmp1 = pytest.fixture(tmp)
tmp2 = pytest.fixture(tmp)


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


def test_main_include_dirs_succeed(tmp1, tmp2):
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
