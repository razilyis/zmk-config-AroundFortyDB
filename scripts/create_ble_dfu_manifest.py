#!/usr/bin/env python3
"""Create a machine-readable manifest for AroundFortyDB BLE DFU artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PACKAGE_NAMES = {
    "right-central": "around_forty_db_right.dfu.zip",
    "left-peripheral": "around_forty_db_left.dfu.zip",
}


def file_metadata(directory: Path, side: str, filename: str) -> dict[str, object]:
    path = directory / filename
    content = path.read_bytes()
    return {
        "side": side,
        "file": filename,
        "sha256": hashlib.sha256(content).hexdigest(),
        "size": len(content),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--run-number", required=True, type=int)
    parser.add_argument("--commit", required=True)
    arguments = parser.parse_args()

    manifest = {
        "schemaVersion": 1,
        "firmwareVersion": f"git-{arguments.commit[:12]}",
        "repository": arguments.repository,
        "branch": arguments.branch,
        "runId": arguments.run_id,
        "runNumber": arguments.run_number,
        "commitSha": arguments.commit,
        "board": "seeeduino_xiao_ble",
        "shield": "around_forty_db",
        "bootloader": "adafruit-nrf52-legacy-dfu",
        "softDeviceRequirement": "0xFFFE",
        "packages": [
            file_metadata(arguments.directory, side, filename)
            for side, filename in PACKAGE_NAMES.items()
        ],
    }

    output = arguments.directory / "firmware-manifest.json"
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Created {output}")


if __name__ == "__main__":
    main()
