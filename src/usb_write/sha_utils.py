"""
A Collection of functions for hashing files and comparing hashes against files
"""

from __future__ import annotations
from usb_write._logging import logger
import hashlib
from typing import Union, List
from pathlib import Path


StringOrBytes = Union[str, bytes]
__all__ = ["hash_file", "validate_hash"]


def hash_file(file: bytes) -> str:
    """Hash bytes with SHA256 into a string"""
    rhash = hashlib.sha256(file)
    return rhash.hexdigest()


def validate_hash(org_hash: str, file: bytes) -> bool:
    """Compare the SHA256 hash of file to org_hash"""
    if not len(org_hash) == 64:
        raise ValueError("org_hash has to be a valid SHA256 hash")
    fhash = hashlib.sha256(file).hexdigest()
    return compare_hashes(org_hash, fhash)


def compare_hashes(orignal: str, file_hash: str) -> bool:
    result: bool = orignal == file_hash
    if not result:
        logger.debug(f"File hash is not the same expected {orignal} got {file_hash}")
    return result


def compare_hashes_for_directory(orignals: List[str], directory: Path) -> bool:
    hashes: List[str] = get_hashes_for_directory(directory)
    if not len(hashes) == len(orignals):
        logger.warn(
            f"the new directory doesnt have enough files expected {len(hashes)} got {len(orignals)}"
        )
        return False
    for orig, new in zip(orignals, hashes):
        if not compare_hashes(orig, new):
            logger.debug("Hashes dont match")
            return False
    return True


def get_hashes_for_directory(directory: Path) -> List[str]:
    hashes: List[str] = []
    for file in directory.absolute().iterdir():
        if not file.is_dir():
            with file.open("rb") as f:
                hashes.append(hash_file(f.read()).join(file.name))
    return hashes


def main() -> int:
    origs = get_hashes_for_directory(Path("."))
    print(f"orignals: {origs}")
    res = compare_hashes_for_directory(origs, Path("."))
    print("Success" if res else "Failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
