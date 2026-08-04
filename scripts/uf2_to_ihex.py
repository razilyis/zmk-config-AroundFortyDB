#!/usr/bin/env python3
"""Convert an application UF2 to address-preserving Intel HEX."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


UF2_BLOCK_SIZE = 512
UF2_MAGIC_START0 = 0x0A324655
UF2_MAGIC_START1 = 0x9E5D5157
UF2_MAGIC_END = 0x0AB16F30
UF2_FLAG_NO_FLASH = 0x00000001
UF2_FLAG_FAMILY_ID_PRESENT = 0x00002000
XIAO_NRF52840_FAMILY_ID = 0xADA52840
XIAO_NRF52840_APPLICATION_START = 0x00027000
NRF52840_FLASH_END = 0x00100000


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a XIAO nRF52840 application UF2 to Intel HEX."
    )
    parser.add_argument("input", type=Path, help="Input UF2 file")
    parser.add_argument("output", type=Path, help="Output Intel HEX file")
    return parser.parse_args()


def load_uf2(path: Path) -> dict[int, int]:
    content = path.read_bytes()
    if not content or len(content) % UF2_BLOCK_SIZE != 0:
        raise ValueError("UF2 size must be a non-zero multiple of 512 bytes")

    image: dict[int, int] = {}
    expected_block_count = len(content) // UF2_BLOCK_SIZE

    for block_index in range(expected_block_count):
        offset = block_index * UF2_BLOCK_SIZE
        block = content[offset : offset + UF2_BLOCK_SIZE]
        (
            magic_start0,
            magic_start1,
            flags,
            target_address,
            payload_size,
            declared_block_number,
            declared_block_count,
            family_id,
        ) = struct.unpack_from("<IIIIIIII", block)
        magic_end = struct.unpack_from("<I", block, UF2_BLOCK_SIZE - 4)[0]

        if (magic_start0, magic_start1, magic_end) != (
            UF2_MAGIC_START0,
            UF2_MAGIC_START1,
            UF2_MAGIC_END,
        ):
            raise ValueError(f"Invalid UF2 magic in block {block_index}")
        if flags & UF2_FLAG_NO_FLASH:
            raise ValueError(f"No-flash UF2 block is not allowed: {block_index}")
        if not flags & UF2_FLAG_FAMILY_ID_PRESENT:
            raise ValueError(f"UF2 family ID is missing in block {block_index}")
        if family_id != XIAO_NRF52840_FAMILY_ID:
            raise ValueError(
                f"Unexpected UF2 family ID 0x{family_id:08X} in block {block_index}"
            )
        if declared_block_number != block_index:
            raise ValueError(
                f"Out-of-order UF2 block: expected {block_index}, "
                f"found {declared_block_number}"
            )
        if declared_block_count != expected_block_count:
            raise ValueError(
                f"UF2 block count mismatch in block {block_index}: "
                f"expected {expected_block_count}, found {declared_block_count}"
            )
        if payload_size == 0 or payload_size > 476:
            raise ValueError(f"Invalid UF2 payload size in block {block_index}")

        payload_end = target_address + payload_size
        if target_address < XIAO_NRF52840_APPLICATION_START:
            raise ValueError(
                f"UF2 writes below application start: 0x{target_address:08X}"
            )
        if payload_end > NRF52840_FLASH_END:
            raise ValueError(f"UF2 writes past nRF52840 flash: 0x{payload_end:08X}")

        payload = block[32 : 32 + payload_size]
        for payload_offset, value in enumerate(payload):
            address = target_address + payload_offset
            previous = image.get(address)
            if previous is not None and previous != value:
                raise ValueError(f"Conflicting UF2 data at 0x{address:08X}")
            image[address] = value

    if not image:
        raise ValueError("UF2 contains no application data")
    if min(image) != XIAO_NRF52840_APPLICATION_START:
        raise ValueError(
            f"Application must start at 0x{XIAO_NRF52840_APPLICATION_START:08X}; "
            f"found 0x{min(image):08X}"
        )

    return image


def make_record(address: int, record_type: int, data: bytes) -> str:
    record = bytes(
        [len(data), (address >> 8) & 0xFF, address & 0xFF, record_type]
    ) + data
    checksum = (-sum(record)) & 0xFF
    return ":" + (record + bytes([checksum])).hex().upper()


def write_ihex(image: dict[int, int], path: Path) -> None:
    lines: list[str] = []
    addresses = sorted(image)
    index = 0
    current_upper: int | None = None

    while index < len(addresses):
        start = addresses[index]
        upper = start >> 16
        if upper != current_upper:
            lines.append(make_record(0, 4, upper.to_bytes(2, "big")))
            current_upper = upper

        data = bytearray([image[start]])
        index += 1
        while index < len(addresses) and len(data) < 16:
            next_address = addresses[index]
            if next_address != start + len(data) or next_address >> 16 != upper:
                break
            data.append(image[next_address])
            index += 1

        lines.append(make_record(start & 0xFFFF, 0, bytes(data)))

    lines.append(make_record(0, 1, b""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")


def main() -> None:
    arguments = parse_arguments()
    image = load_uf2(arguments.input)
    write_ihex(image, arguments.output)
    print(
        f"Converted {arguments.input.name}: {len(image)} bytes, "
        f"0x{min(image):08X}-0x{max(image):08X} -> {arguments.output}"
    )


if __name__ == "__main__":
    main()
