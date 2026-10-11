"""
tests.verify_dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

AST-based static analyzer verifying zero external dependencies in apex_cua.
Asserts that 100% of imports are from Python standard library or internal apex_cua packages.
"""

import os
import ast
import sys
from typing import Set, List, Tuple

# Python 3.9+ standard library top-level modules
STDLIB_MODULES = {
    "abc", "argparse", "array", "ast", "asyncio", "base64", "binascii", "bisect",
    "builtins", "bz2", "calendar", "cmath", "cmd", "code", "codecs", "collections",
    "colorsys", "compileall", "concurrent", "configparser", "contextlib", "contextvars",
    "copy", "copyreg", "cProfile", "crypt", "csv", "ctypes", "curses", "dataclasses",
    "datetime", "dbm", "decimal", "difflib", "dis", "distutils", "doctest", "email",
    "encodings", "ensurepip", "enum", "errno", "faulthandler", "fcntl", "filecmp",
    "fileinput", "fnmatch", "formatter", "fractions", "ftplib", "functools", "gc",
    "getopt", "getpass", "gettext", "glob", "graphlib", "grp", "gzip", "hashlib",
    "heapq", "hmac", "html", "http", "idlelib", "imaplib", "imghdr", "imp",
    "importlib", "inspect", "io", "ipaddress", "itertools", "json", "keyword",
    "lib2to3", "linecache", "locale", "logging", "lzma", "mailbox", "mailcap",
    "marshal", "math", "mimetypes", "mmap", "modulefinder", "msilib", "msvcrt",
    "multiprocessing", "netrc", "nis", "nntplib", "numbers", "operator", "optparse",
    "os", "ossaudiodev", "parser", "pathlib", "pdb", "pickle", "pickletools",
    "pipes", "pkgutil", "platform", "plistlib", "poplib", "posix", "posixpath",
    "pprint", "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc",
    "queue", "quopri", "random", "re", "readline", "reprlib", "resource", "rlcompleter",
    "runpy", "sched", "secrets", "select", "selectors", "shelve", "shlex", "shutil",
    "signal", "site", "smtpd", "smtplib", "sndhdr", "socket", "socketserver",
    "spwd", "sqlite3", "ssl", "stat", "statistics", "string", "stringprep", "struct",
    "subprocess", "sunau", "symbol", "symtable", "sys", "sysconfig", "syslog",
    "tabnanny", "tarfile", "telnetlib", "tempfile", "termios", "test", "textwrap",
    "threading", "time", "timeit", "tkinter", "token", "tokenize", "trace",
    "traceback", "tracemalloc", "tty", "turtle", "turtledemo", "types", "typing",
    "unicodedata", "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave",
    "weakref", "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml",
    "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib", "_thread",
}


def scan_file_imports(filepath: str) -> List[Tuple[str, int]]:
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                imports.append((root_pkg, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                imports.append((root_pkg, node.lineno))
    return imports


def verify_package_clean(package_dir: str) -> bool:
    violations = []
    for root, _, files in os.walk(package_dir):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                imports = scan_file_imports(path)
                for root_pkg, lineno in imports:
                    if root_pkg == "apex_cua":
                        continue
                    if root_pkg not in STDLIB_MODULES:
                        violations.append((path, lineno, root_pkg))

    if violations:
        print("DEPENDENCY VIOLATIONS FOUND:")
        for path, lineno, pkg in violations:
            print(f"  {path}:{lineno} -> imported non-stdlib '{pkg}'")
        return False

    print("VERIFICATION SUCCESS: 100% pure standard library. Zero external dependencies.")
    return True


if __name__ == "__main__":
    pkg_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apex_cua")
    if not verify_package_clean(pkg_root):
        sys.exit(1)
    sys.exit(0)
