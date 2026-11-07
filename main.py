"""Project entry point for training and reporting the ENSO forecast ensemble."""

from __future__ import annotations

import argparse
import json

from src.pipeline import run_full_pipeline


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--horizons",
        nargs="+",
        type=int,
        choices=(1, 3, 6),
        default=(1, 3, 6),
    )
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--prepare-data",
        action="store_true",
        help="Run src/preprocessing.py before training.",
    )
    parser.add_argument(
        "--run-eda",
        action="store_true",
        help="Run src/etl.py and src/utils.py conversion and EDA.",
    )
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    report = run_full_pipeline(
        horizons=tuple(args.horizons),
        epochs=args.epochs,
        seed=args.seed,
        prepare_data=args.prepare_data,
        run_eda=args.run_eda,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
