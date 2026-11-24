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
        "--autoscrap",
        action="store_true",
        default=False,
        help="Download latest remote climate sources before QC and training. Default: False (use local data).",
    )
    parser.add_argument(
        "--append-data",
        type=str,
        default=None,
        help="Path to new observations CSV to incrementally append to master archive without rewriting historical data.",
    )
    parser.add_argument(
        "--retrain-full",
        action="store_true",
        help="Retrain all models from scratch on the full expanding window without xgb_model warm start.",
    )
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
    parser.add_argument(
        "--legacy-training",
        action="store_true",
        help="Use the original fixed train/validation/test training pipeline instead of temporal backtesting.",
    )
    parser.add_argument(
        "--final-retrain",
        action="store_true",
        help="Retrain the frozen validation-selected models on all eligible history and forecast supported leads.",
    )
    parser.add_argument(
        "--forecast-months",
        type=int,
        default=None,
        help="Forecast support window in months (default: 18 in final retraining mode).",
    )
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()
    if args.append_data:
        from src.incremental import update_pipeline_and_retrain

        report = update_pipeline_and_retrain(
            new_data=args.append_data,
            horizons=tuple(args.horizons),
            epochs=args.epochs,
            seed=args.seed,
            force_retrain=args.retrain_full,
        )
        print(json.dumps(report, indent=2))
        return
    if args.retrain_full:
        from src.incremental import retrain_from_full_data

        report = retrain_from_full_data(
            horizons=tuple(args.horizons),
            epochs=args.epochs,
            seed=args.seed,
        )
        print(json.dumps(report, indent=2))
        return
    if args.final_retrain or args.forecast_months is not None:
        from src.ml.final_retraining import run_final_retraining

        report = run_final_retraining(
            forecast_months=(
                args.forecast_months
                if args.forecast_months is not None
                else 18
            ),
        )
        print(json.dumps(report, indent=2))
        return
    report = run_full_pipeline(
        horizons=tuple(args.horizons),
        epochs=args.epochs,
        seed=args.seed,
        prepare_data=args.prepare_data,
        run_eda=args.run_eda,
        legacy_training=args.legacy_training,
        autoscrap=args.autoscrap,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
