import numpy as np
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar
from sqlalchemy import text

from src.config import DA_CONFIG
from utils import ConnectMysql


def rfm_analysis():
    """
    RF 分层（数据集不含金额，M 维度缺省）。

    打分方向统一为「越高越好」：
      R：最近一次购买越近，分数越高（3 = 最近 25%）
      F：购买次数越多，分数越高（1 次 = 1，2~3 次 = 2，4 次及以上 = 3）

    原来的写法 R 用 labels_reverse=[3,2,1]，最近购买反而拿低分，
    和 F 的方向相反，RF 组合不好解释，已统一。
    """
    engine = ConnectMysql().get_engine()
    data = pd.read_sql(
        text(f"SELECT user_id, behavior, datetime FROM {DA_CONFIG['table']}"), engine
    )
    buyers = (
        data[data["behavior"] == "buy"]
        .groupby("user_id")
        .agg(R=("datetime", "max"), F=("datetime", "size"))
        .reset_index()
    )
    del data

    desc = buyers["R"].describe()
    r_bin = [desc["min"], desc["50%"], desc["75%"], desc["max"]]
    buyers["R_score"] = pd.cut(buyers["R"], bins=r_bin, labels=[1, 2, 3], include_lowest=True)
    buyers["F_score"] = pd.cut(
        buyers["F"], bins=[0, 1, 3, np.inf], labels=[1, 2, 3], right=True
    )
    buyers["RF"] = buyers["R_score"].astype(str) + buyers["F_score"].astype(str)

    seg = (
        buyers.groupby("RF")
        .agg(人数=("user_id", "size"), 占比=("user_id", lambda s: len(s) / len(buyers)))
        .reset_index()
        .sort_values("RF")
    )
    seg["占比"] = seg["占比"].map(lambda v: f"{v:.1%}")

    bar = (
        Bar()
        .add_xaxis(seg["RF"].tolist())
        .add_yaxis(
            "人数",
            seg["人数"].tolist(),
            label_opts=opts.LabelOpts(position="top", is_show=True),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"RF 分层（{len(buyers):,} 名购买用户，R/F 均为分越高越好）"
            ),
            xaxis_opts=opts.AxisOpts(type_="category", name="RF"),
            yaxis_opts=opts.AxisOpts(name="人数"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    bar.render(DA_CONFIG["output_dir"] / "RF.html")
    return bar, seg
