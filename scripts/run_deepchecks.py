from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from deepchecks.tabular import Dataset
from deepchecks.tabular.checks import FeatureDrift, LabelDrift, TrainTestPerformance
from deepchecks.tabular.suite import Suite
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


TARGETS = ("price actual", "total load actual")


def slugify(text: str) -> str:
    return text.lower().replace(" ", "_").replace("/", "_")


def load_frame(csv_path: Path, max_rows: int | None) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
        df = df.sort_values("time")

    if max_rows is not None and len(df) > max_rows:
        df = df.head(max_rows).copy()

    return df.copy()


def prepare_frame(df: pd.DataFrame, target: str) -> pd.DataFrame:
    frame = df.drop(columns=["time"], errors="ignore").copy()
    frame = frame.dropna(subset=[target]).copy()
    frame = frame.fillna(frame.median(numeric_only=True))
    return frame


def validate_data_integrity(df: pd.DataFrame, target: str) -> dict:
    """Check data integrity: nulls, duplicates, value ranges, and statistics."""
    issues = []
    warnings = []

    # Check for excessive nulls
    null_ratios = df.isnull().sum() / len(df)
    for col, ratio in null_ratios.items():
        if ratio > 0.5:
            issues.append(f"Column '{col}' has {ratio*100:.1f}% null values")
        elif ratio > 0.1:
            warnings.append(f"Column '{col}' has {ratio*100:.1f}% null values")

    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        warnings.append(f"Found {duplicates} duplicate rows")

    # Check target column statistics
    if target in df.columns:
        target_data = df[target].dropna()
        if len(target_data) == 0:
            issues.append(f"Target column '{target}' has no valid values")
        else:
            if target_data.std() == 0:
                issues.append(f"Target column '{target}' has zero variance")
            if (target_data < 0).any():
                warnings.append(f"Target column '{target}' contains negative values")

    # Check numeric columns for all NaN or constant values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().all():
            issues.append(f"Column '{col}' is entirely null")
        elif df[col].nunique() <= 1:
            warnings.append(f"Column '{col}' has only one unique value (low variance)")

    return {
        "issues": issues,
        "warnings": warnings,
        "passed": len(issues) == 0,
    }


def build_suite() -> Suite:
    feature_drift = FeatureDrift()
    feature_drift.add_condition_drift_score_less_than(
        max_allowed_numeric_score=0.95,
        max_allowed_categorical_score=0.95,
    )

    label_drift = LabelDrift()
    label_drift.add_condition_drift_score_less_than(max_allowed_drift_score=0.35)

    performance = TrainTestPerformance(scorers=["r2"])
    performance.add_condition_test_performance_greater_than(min_score=0.0)

    return Suite("CI Validation", feature_drift, label_drift, performance)


def run_target_checks(df: pd.DataFrame, target: str, output_dir: Path) -> dict:
    frame = prepare_frame(df, target)

    feature_columns = [
        column
        for column in frame.columns
        if column not in {target, *TARGETS}
    ]

    if len(feature_columns) == 0:
        raise ValueError(f"No features available for target '{target}'.")

    split_index = max(1, int(len(frame) * 0.8))
    if split_index >= len(frame):
        split_index = len(frame) - 1

    train = frame.iloc[:split_index].copy()
    test = frame.iloc[split_index:].copy()

    if len(test) == 0:
        raise ValueError(f"Not enough rows to split train/test for target '{target}'.")

    train_dataset = Dataset(
        train,
        label=target,
        features=feature_columns,
        cat_features=[],
    )
    test_dataset = Dataset(
        test,
        label=target,
        features=feature_columns,
        cat_features=[],
    )

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train[feature_columns], train[target])

    predictions = model.predict(test[feature_columns])
    metrics = {
        "r2": float(r2_score(test[target], predictions)),
        "mae": float(mean_absolute_error(test[target], predictions)),
        "rmse": float(np.sqrt(mean_squared_error(test[target], predictions))),
    }

    suite = build_suite()
    result = suite.run(train_dataset, test_dataset, model=model, with_display=False)

    target_dir = output_dir / slugify(target)
    target_dir.mkdir(parents=True, exist_ok=True)
    html_path = target_dir / "deepchecks_report.html"
    json_path = target_dir / "deepchecks_report.json"
    result.save_as_html(str(html_path))
    json_path.write_text(result.to_json(), encoding="utf-8")

    suite_data = json.loads(result.to_json())
    condition_statuses = []
    for check_result in suite_data.get("results", []):
        condition_statuses.extend(
            [item.get("Status", "UNKNOWN") for item in check_result.get("conditions_results", [])]
        )

    passed = all(status == "PASS" for status in condition_statuses) if condition_statuses else True

    return {
        "target": target,
        "rows": len(frame),
        "train_rows": len(train),
        "test_rows": len(test),
        "metrics": metrics,
        "passed": passed,
        "html_report": str(html_path),
        "json_report": str(json_path),
        "condition_statuses": condition_statuses,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DeepChecks validation on the energy dataset.")
    parser.add_argument("--data", default="energy_dataset.csv", help="Path to the source CSV dataset.")
    parser.add_argument(
        "--output-dir",
        default="artifacts/deepchecks",
        help="Directory where DeepChecks reports will be written.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=5000,
        help="Maximum number of chronological rows to validate for CI speed.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail the process when data integrity or DeepChecks conditions do not pass.",
    )
    args = parser.parse_args()

    data_path = Path(args.data)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frame = load_frame(data_path, args.max_rows)
    results = []

    # Phase 1: Data Integrity Validation
    print("\n=== PHASE 1: Data Integrity Validation ===")
    integrity_results = {}
    for target in TARGETS:
        if target not in frame.columns:
            print(f"Skipping {target}: column not found.")
            continue
        integrity = validate_data_integrity(frame, target)
        integrity_results[target] = integrity
        print(f"\n{target}:")
        if integrity["issues"]:
            print(f"  ISSUES: {integrity['issues']}")
        if integrity["warnings"]:
            print(f"  WARNINGS: {integrity['warnings']}")
        if integrity["passed"]:
            print(f"  ✓ Data integrity passed")

    # Phase 2: Drift and Performance Validation
    print("\n=== PHASE 2: Drift & Performance Validation ===")
    for target in TARGETS:
        if target not in frame.columns:
            print(f"Skipping {target}: column not found.")
            continue
        result = run_target_checks(frame, target, output_dir)
        results.append(result)
        print(
            f"{target}: r2={result['metrics']['r2']:.4f}, mae={result['metrics']['mae']:.4f}, "
            f"rmse={result['metrics']['rmse']:.4f}, passed={result['passed']}"
        )
        print(f"Reports: {result['html_report']} | {result['json_report']}")

    summary_path = output_dir / "deepchecks_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSummary written to {summary_path}")

    integrity_path = output_dir / "data_integrity_report.json"
    integrity_path.write_text(json.dumps(integrity_results, indent=2), encoding="utf-8")
    print(f"Data integrity report written to {integrity_path}")

    if not results:
        raise SystemExit("No DeepChecks targets were validated.")

    # In non-strict mode we still produce reports, but we do not fail the
    # command. This keeps final/manual runs green while CI can opt into strict
    # failure semantics.
    has_integrity_issues = any(not integrity["passed"] for integrity in integrity_results.values())
    has_deepchecks_issues = any(not result["passed"] for result in results)

    if args.strict and (has_integrity_issues or has_deepchecks_issues):
        print("\n❌ VALIDATION FAILED")
        raise SystemExit(1)

    if has_integrity_issues or has_deepchecks_issues:
        print("\n⚠ VALIDATION COMPLETED WITH ISSUES (non-strict mode)")
        return 0

    print("\n✓ ALL VALIDATIONS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())