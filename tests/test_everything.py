import pytest
from mash import *


@pytest.fixture
def toc():
    return {"test": []}


@pytest.fixture
def markdown():
    return find_markdown("notes")


@pytest.fixture
def config():
    return load_config_file()


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
            ".png",
        ),
    ]


def test_create_tables_of_contents(markdown):
    assert create_tables_of_contents(markdown) == {
        "": ["Example Page"],
        "Session Recaps": [
            "Session 0",
            "Session 1",
            "Session 10",
            "Session 11",
            "Session 2",
        ],
    }
