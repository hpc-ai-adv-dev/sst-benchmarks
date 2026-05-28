#!/usr/bin/env python3
"""Generate a filesystem-safe base filename from a container URI."""

import argparse
import re


def generate_filename(uri: str) -> str:
    """Return a normalized base filename from a container URI."""
    parts = uri.split("/")
    if len(parts) >= 2:
        base_name = "/".join(parts[-2:])
    else:
        base_name = parts[0]

    if ":" not in base_name:
        base_name = f"{base_name}:latest"

    base_name = base_name.replace(":", "-").replace("/", "-")
    base_name = re.sub(r"[^a-zA-Z0-9._-]", "_", base_name)
    base_name = re.sub(r"_+", "_", base_name)
    base_name = re.sub(r"^_|_$", "", base_name)
    return base_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a filesystem-safe base filename from a container URI.",
    )
    parser.add_argument("container_uri", help="Container URI, e.g. docker.io/ubuntu:22.04")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(generate_filename(args.container_uri))


if __name__ == "__main__":
    main()
