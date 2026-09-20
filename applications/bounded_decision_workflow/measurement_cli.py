"""Measurement-only delivery commands for Slice 5; legacy CLI is untouched."""

import argparse
from pathlib import Path

from .measurement_delivery import replay_measurement_bundle, verify_measurement_bundle


def main(argv=None):
    parser = argparse.ArgumentParser(prog="measurement-delivery")
    sub = parser.add_subparsers(dest="operation", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--bundle", required=True)
    replay = sub.add_parser("replay")
    replay.add_argument("--bundle", required=True)
    for name in ("build", "policy", "result", "trace"):
        replay.add_argument("--" + name, required=True)
    args = parser.parse_args(argv)
    if args.operation == "verify":
        bundle = verify_measurement_bundle(args.bundle)
    else:
        read = lambda name: Path(getattr(args, name)).read_bytes()
        bundle = replay_measurement_bundle(
            args.bundle, build=read("build"), policy=read("policy"),
            result=read("result"), trace=read("trace"))
    print(bundle.manifest_sha256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
