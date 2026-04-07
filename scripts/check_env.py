from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODULES = [
    "openai",
    "pandas",
    "numpy",
    "pydantic",
    "yaml",
    "jsonschema",
    "tqdm",
]


def main() -> None:
    missing = []
    for module_name in MODULES:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(module_name)

    if missing:
        raise SystemExit(f"Missing modules: {', '.join(missing)}")

    print("Environment check passed.")


if __name__ == "__main__":
    main()
