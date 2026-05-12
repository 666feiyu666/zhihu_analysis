from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATA_DIR = PROJECT_ROOT / "original_data"
NETWORK_DIR = PROJECT_ROOT / "network"
LABELING_DIR = PROJECT_ROOT / "labeling"
NETWORK_OUTPUTS_DIR = NETWORK_DIR / "outputs"
LABELING_OUTPUTS_DIR = LABELING_DIR / "outputs"


def ensure_output_dirs() -> None:
    NETWORK_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    LABELING_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def find_data_file(preferred_name: str, fallback_relative_paths: list[str]) -> Path:
    """Find a data file, preferring original_data but allowing legacy locations."""
    candidates = [ORIGINAL_DATA_DIR / preferred_name]
    candidates.extend(PROJECT_ROOT / rel for rel in fallback_relative_paths)
    for path in candidates:
        if path.exists():
            return path
    searched = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Could not find {preferred_name}. Searched:\n{searched}")

