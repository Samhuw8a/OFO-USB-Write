from __future__ import annotations
from typing import List, Optional
from pathlib import Path
from argparse import ArgumentParser, Namespace
from usb_write._logging import logger, debug_conf, no_conf
from usb_write.file_copy import get_usb_drives, copy_files_to_volumes
import os


def clear() -> None:
    if os.name == "posix":
        os.system("clear")
    elif os.name == "nt":
        os.system("cls")


def _init_argparser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser(
        prog="OFO-USB",
        description="Ein Programm, dass den Inhalt eines Ordner auf viele USB-Sticks kopiert.",
    )
    parser.add_argument("lagerfilm_dir", type=Path)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose Stdout output"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="debug Stdout output"
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path("/Volumes/"),
        help="folder where the volumes can be found",
    )
    return parser


def run(args: Namespace) -> None:
    if not args.lagerfilm_dir.is_dir():
        raise NotADirectoryError(f"{args.lagerfilm_dir} is not a directory")

    target_dir: Optional[str] = None
    if os.name == "posix":
        target_dir = input("Wie heissen die zu überschreibenden USB-Sticks?: ")

    usb_volumes: List[Path] = get_usb_drives(os.name, target_dir, args.dest)

    print(f'Kopiere alle Dateien in \n{args.lagerfilm_dir}" nach:')
    for d in usb_volumes:
        if os.name == "nt":
            print(d.drive)
        print(d.name)

    if input("[Y/n]: ").lower() == "n":
        raise KeyboardInterrupt("User aborted copy process")

    logger.info("Starte das Kopieren der Daten")
    copy_files_to_volumes(args.lagerfilm_dir, usb_volumes)


def main(*argv: str) -> int:
    parser = _init_argparser()
    args = parser.parse_args(argv or None)

    if args.debug:
        debug_conf()
    elif not args.verbose:
        no_conf()

    logger.debug("Finished parsing command line arguments")

    try:
        run(args)
    except Exception as e:
        logger.critical(f"Fehler beim Kopieren der Dateien: {e}")
        logger.debug("Aborting program due to error")
        return 1

    logger.info("Finished copying files to all USB drives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
