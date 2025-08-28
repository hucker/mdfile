# src/mdfile/__init__.py
"""
mdfile — Markdown File Manipulation Package
"""
from importlib.metadata import version

from util.dotted_dict import DottedDict

from .md_updater import update_markdown_file
from updater.ignore import IgnoreBlocks
from updater.variables import VarReplacer
from updater.process import ProcessReplacer
from updater.process import ProcessBlockReplacer
from mdfile.to_md.md_factory import markdown_factory
from updater.files import FileBlockInsertReplacer
from updater.files import FileReplacer
from updater.process import ShellReplacer
from updater.process import ShellBlockReplacer

from to_md.code_to_md import CodeToMarkdown
from to_md.csv_to_md import  CsvToMarkdown
from to_md.json_to_md import JsonToMarkdown
from to_md.md_to_md import MarkdownToMarkdown
from to_md.text_to_md import TextToMarkdown
from to_md.to_markdown import ToMarkdown

__version__ = version("mdfile")
__author__ = "Chuck Bass"
__email__ = "chuck@acrocad.net"

__all__ = ["update_markdown_file",
           "IgnoreBlocks",
           "VarReplacer",
           "ProcessReplacer",
           "ProcessBlockReplacer",
           "ShellReplacer",
           "ShellBlockReplacer",
           "FileBlockInsertReplacer",
           "FileReplacer",
           "CodeToMarkdown",
           "CsvToMarkdown",
           "JsonToMarkdown",
           "MarkdownToMarkdown",
           "TextToMarkdown",
           "ToMarkdown",
           "markdown_factory",
           "DottedDict",
           "__version__",
           "__author__",
           "__email__"]
