from __future__ import annotations
from typing import List
from pathlib import Path
from argparse import ArgumentParser
import concurrent.futures
import os
import shutil
import psutil


VOLUMES: str = "./test/volumes/"


def clear() -> None:
    if os.name == "posix":
        os.system("clear")
    elif os.name == "nt":
        os.system("cls")


def empty_dir(dir: Path) -> bool:
    return list(dir.iterdir()) == []


def _init_argparser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser(
        prog="OFO-USB",
        description="Ein Programm, dass den Inhalt eines Ordner auf viele USB-Sticks kopiert."
    )
    parser.add_argument("lagerfilm_dir", type=Path)
    return parser


def windows_get_all_removable_devices() -> List[Path]:
    return list(map(lambda x: Path(x.mountpoint), filter(lambda x: "removable" in x.opts, psutil.disk_partitions())))


def get_all_empty_Volumes_from_name(volumename: str) -> List[Path]:
    """Returns all empty sub directories"""
    all_volumes: Path = Path(VOLUMES)
    filterd_volumes = filter(
        lambda x: x.name.startswith(volumename) and x.is_dir() and empty_dir(x), all_volumes.iterdir())
    return list(filterd_volumes)


def copy_file_to(src: Path, dst: Path) -> str:
    shutil.copytree(src, dst, dirs_exist_ok=True)
    return f"{dst.name}: OK"


def copy_files_to_Volumes(target_directory: Path, volumes: List[Path]) -> None:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        processes = []
        for vol in volumes:
            processes.append(executor.submit(
                copy_file_to, target_directory, vol))

        for p in concurrent.futures.as_completed(processes):
            print(p.result())

    print("Fertig mit Kopieren")


def main(*argv: str) -> int:
    parser = _init_argparser()
    args = parser.parse_args(argv or None)

    if not args.lagerfilm_dir.is_dir():
        print("lagerfilm_dir muss ein Ordner sein")
        return 1
    clear()
    if os.name == "posix":
        target_dir = input("Wie heissen die zu überschreibenden USB-Sticks?: ")
        usb_volumes = get_all_empty_Volumes_from_name(target_dir)

        if len(usb_volumes) == 0:
            print("Es gibt keine USB-Sticks die den Kriterien entsprechen")
            return 1

        print(f"Kopiere alle Dateien in \n{args.lagerfilm_dir}\" nach:")
        for i in usb_volumes:
            print(i.name)
    elif os.name == "nt":
        usb_volumes = windows_get_all_removable_devices()
        if len(usb_volumes) == 0:
            print("Es gibt keine USB-Sticks die den Kriterien entsprechen")
            return 1

        print(f"Kopiere alle Dateien in \n{args.lagerfilm_dir}\" nach:")
        for i in usb_volumes:
            print(i.drive)
    else:
        raise EnvironmentError("OS not compatible")

    if input("[Y/n]: ").lower() == "n":
        return 1

    print("!!!WICHTIG!!!, Hol dir ein Bier!")
    print("Starte das Kopieren der Daten:")
    copy_files_to_Volumes(args.lagerfilm_dir, usb_volumes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main("./test/lagerfilm/"))
