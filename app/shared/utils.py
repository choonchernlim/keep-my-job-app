from pathlib import Path

DATA_PATH = Path.cwd().parent.parent / "data"

# fail if data path does not exist
if not DATA_PATH.exists():
    raise ValueError(f"Data path [{DATA_PATH}] does not exist.")


def get_data_dir_path() -> Path:
    return DATA_PATH
