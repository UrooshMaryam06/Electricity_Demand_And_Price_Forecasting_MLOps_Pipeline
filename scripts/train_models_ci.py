"""CI/CD model training script: trains ML models and validates them."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path so we can import train_pipeline
sys.path.insert(0, str(Path(__file__).parent.parent))

from train_pipeline import build_and_run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Train ML models for CI/CD pipeline.")
    parser.add_argument("--data", default="energy_dataset.csv", help="Path to the source CSV dataset.")
    parser.add_argument("--artifacts", default="artifacts", help="Directory where artifacts will be saved.")
    args = parser.parse_args()

    data_path = Path(args.data)
    artifacts_dir = Path(args.artifacts)

    if not data_path.exists():
        print(f"ERROR: Data file not found: {data_path}")
        return 1

    print(f"🚀 Starting model training...")
    print(f"   Data: {data_path}")
    print(f"   Artifacts: {artifacts_dir}")

    try:
        result = build_and_run_pipeline(data_path, artifacts_dir)
        metadata_path = result.get("metadata_path")
        
        print(f"✓ Model training completed successfully")
        print(f"  Metadata saved to: {metadata_path}")
        
        # Save training metadata for workflow
        ci_metadata = {
            "status": "success",
            "metadata_path": metadata_path,
            "timestamp": str(Path(__file__).stat().st_mtime),
        }
        ci_meta_path = artifacts_dir / "ci_train_metadata.json"
        ci_meta_path.write_text(json.dumps(ci_metadata, indent=2), encoding="utf-8")
        print(f"  CI metadata saved to: {ci_meta_path}")
        
        return 0
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
