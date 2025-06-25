import re
import pathlib
from typing import List, Optional, Union


def get_cwd():
    """
    Return the current working directory.

    Returns
    -------
    pathlib.Path
        Path object pointing to the current working directory.
    """
    return pathlib.Path.cwd()


def find_folders(path: Union[str, pathlib.Path], pattern: Optional[str] = None) -> List[pathlib.Path]:
    """
    Find folders under `path`, optionally matching a regular-expression pattern,
    using pathlib.Path explicitly.

    Parameters
    ----------
    path : str or pathlib.Path
        The directory in which to search for folders.
    pattern : str, optional
        A regular-expression. If given, only folders whose names match
        (re.search) this pattern are returned. If None, all non-invisible
        folders (those not starting with '.') are returned.

    Returns
    -------
    List[pathlib.Path]
        A list of pathlib.Path objects pointing to folders satisfying the criteria.
    """
    base = pathlib.Path(path)
    regex = re.compile(pattern) if pattern is not None else None
    results: List[pathlib.Path] = []

    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        name = entry.name
        if regex:
            if regex.search(name):
                results.append(entry)
        else:
            # skip invisible folders
            if not name.startswith('.'):
                results.append(entry)

    return results

