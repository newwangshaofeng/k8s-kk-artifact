from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

EXCLUDED_IMAGES_BY_ARCH = {
    "arm64": (
        "docker.io/hybridnetdev/hybridnet",
        "hybridnetdev/hybridnet",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, dest="input_path")
    parser.add_argument("--output", required=True, dest="output_path")
    parser.add_argument("--arch", required=True, choices=("amd64", "arm64"))
    return parser.parse_args()


def normalize_operating_systems(items: Any, arch: str) -> Any:
    if not isinstance(items, list):
        return items

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            normalized.append(item)
            continue

        current_arch = item.get("arch")
        if current_arch not in (None, "", arch):
            continue

        updated = dict(item)
        updated["arch"] = arch
        normalized.append(updated)

    return normalized


def normalize_images(items: Any, arch: str) -> Any:
    if not isinstance(items, list):
        return items

    excluded_images = EXCLUDED_IMAGES_BY_ARCH.get(arch, ())
    normalized = []
    for item in items:
        if isinstance(item, str) and any(excluded in item for excluded in excluded_images):
            continue

        normalized.append(item)

    return normalized


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)

    with input_path.open("r", encoding="utf-8") as file:
        manifest = yaml.safe_load(file)

    if not isinstance(manifest, dict):
        raise ValueError("manifest content must be a YAML mapping")

    spec = manifest.setdefault("spec", {})
    if not isinstance(spec, dict):
        raise ValueError("manifest.spec must be a YAML mapping")

    spec["arches"] = [args.arch]

    if "operatingSystems" in spec:
        spec["operatingSystems"] = normalize_operating_systems(spec.get("operatingSystems"), args.arch)

    if "images" in spec:
        spec["images"] = normalize_images(spec.get("images"), args.arch)

    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        yaml.safe_dump(manifest, file, allow_unicode=True, sort_keys=False)


if __name__ == "__main__":
    main()
