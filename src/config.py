from pathlib import Path

DA_CONFIG = {
    "data_path": Path(__file__).parent.parent / "data" / "UserBehavior.csv",
    "output_dir": Path(__file__).parent.parent / "data",
    "date": {"start": "2017-11-25", "end": "2017-12-03"},
    # 分析所用的表。
    # userbehavior_usersample：按 user_id 抽样、保留用户完整行为序列（推荐，转化率可信）
    # userbehavior：原来的按行抽样表（每用户平均只有 1.9 条，转化率会被严重压低）
    "table": "userbehavior_usersample",
}
