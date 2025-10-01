from __future__ import annotations
from typing import List
from pathlib import Path
from argparse import ArgumentParser
import os

VOLUMES: str = "/Volumes/"


def empty_dir(dir: Path) -> bool:
    return list(dir.iterdir()) == []


def _init_argparser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser(
        prog="OFO-USB",
        description="Ein Programm, dass den Inhalt eines Ordner auf viele USB-Sticks kopiert."
    )
    parser.add_argument("lagerfilm_dir", type=Path)
    return parser


def get_all_empty_Volumes_from_name(volumename: str) -> List[Path]:
    """Returns all empty sub directories"""
    if os.name == "posix":
        all_volumes: Path = Path(VOLUMES)
    else:
        return []

    filterd_volumes = filter(
        lambda x: x.name.startswith(volumename) and x.is_dir() and empty_dir(x), all_volumes.iterdir())
    return list(filterd_volumes)


def copy_files_to_Volumes(file: Path, volumes: List[Path]) -> None:
    pass


def main(*argv: str) -> int:
    parser = _init_argparser()
    args = parser.parse_args(argv or None)

    if not args.lagerfilm_dir.is_dir():
        print("lagerfilm_dir muss ein Ordner sein")
        return 1
    target_dir = input("Wie heissen die zu überschreibenden USB-Sticks?: ")
    usb_volumes = get_all_empty_Volumes_from_name(target_dir)
    print(usb_volumes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
