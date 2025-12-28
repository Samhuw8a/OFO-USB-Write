from __future__ import annotations
from pathlib import Path
from psutil import disk_partitions
from typing import Optional, List
from usb_write import logger
import concurrent.futures
import shutil


def get_usb_drives(os_name: str, volumename: Optional[str] = None) -> list[Path]:
    match os_name:
        case "posix":
            logger.debug("Getting USB drives for posix system")
            if volumename is None:
                raise ValueError("volumename must be provided for posix systems")

            logger.debug(f"Looking for volumes starting with '{volumename}'")
            all_volumes: Path = Path("/Volumes/")
            filterd_volumes = filter(
                lambda x: x.name.startswith(volumename) and x.is_dir(),
                all_volumes.iterdir())
            usb_volumes = list(filterd_volumes)

        case "nt":
            logger.debug("Getting USB drives for windows system")
            logger.debug("Looking for removable drives")
            usb_volumes = list(map(lambda x: Path(x.mountpoint), filter(
                lambda x: "removable" in x.opts, disk_partitions())))
        case _:
            raise NotImplementedError(f"OS '{os_name}' is not supported")

    logger.debug(f"Found {len(usb_volumes)} USB drives")
    if len(usb_volumes) == 0:
        raise RuntimeError("No USB drives found")

    return usb_volumes


def copy_func(src: Path, dst: Path) -> str:
    # TODO: custom copy function with progress bar
    shutil.copytree(src, dst, dirs_exist_ok=True)
    return f"{dst.name}: OK"


def copy_files_to_volumes(from_dir: Path, to_dir: List[Path]) -> None:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        processes = []
        for vol in to_dir:
            processes.append(executor.submit(
                copy_func, from_dir, vol))

        for p in concurrent.futures.as_completed(processes):
            print(p.result())

    print("Fertig mit Kopieren")
