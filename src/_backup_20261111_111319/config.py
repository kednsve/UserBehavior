from pathlib import Path

DA_CONFIG = {
    "data_path": Path(__file__).parent.parent / "data" / "UserBehavior.csv",
    "output_dir": Path(__file__).parent.parent / "data",
    "date": {"start": "2017-11-25", "end": "2017-12-03"},
}
