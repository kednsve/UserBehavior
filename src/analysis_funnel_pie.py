import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Funnel, Pie
from sqlalchemy import text

from src.config import DA_CONFIG
from utils import ConnectMysql


def analysis_funnel_pie():
    """
    漏斗 + 行为分布饼图。

    漏斗按「去重用户数」计算。收藏和加购是并列行为（没有先后），
    所以漏斗是三步：浏览 → 意向（收藏或加购）→ 购买，
    而不是把收藏、加购硬排成先后两步。
    """
    engine = ConnectMysql().get_engine()
    data = pd.read_sql(
        text(f"SELECT user_id, behavior FROM {DA_CONFIG['table']}"), engine
    )

    pv = set(data.loc[data["behavior"] == "pv", "user_id"])
    fav = set(data.loc[data["behavior"] == "fav", "user_id"])
    cart = set(data.loc[data["behavior"] == "cart", "user_id"])
    buy = set(data.loc[data["behavior"] == "buy", "user_id"])
    intent = fav | cart

    # 漏斗的数据源：每一步是「到这一步为止的去重用户数」
    steps = [
        ("浏览", len(pv)),
        ("意向（收藏或加购）", len(intent)),
        ("购买", len(buy)),
    ]
    base = steps[0][1] or 1
    funnel_data = [
        [f"{name} {cnt:,} 人（{cnt / base:.1%}）", cnt] for name, cnt in steps
    ]

    funnel = (
        Funnel()
        .add("用户转化", funnel_data, sort_="none", gap=2)
        .set_series_opts(
            label_opts=opts.LabelOpts(position="inside", formatter="{b}", color="#fff")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"用户转化漏斗（浏览→购买 {len(buy) / base:.1%}）"
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    funnel.render(DA_CONFIG["output_dir"] / "用户转化漏斗图.html")

    pie_data = [
        ["浏览", len(pv)],
        ["收藏", len(fav)],
        ["加购", len(cart)],
        ["购买", len(buy)],
    ]
    pie = (
        Pie()
        .add("行为分布", pie_data)
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c} 人（{d}%）")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="用户行为分布（去重用户数）"),
            legend_opts=opts.LegendOpts(orient="horizontal", pos_bottom="0%"),
        )
    )
    pie.render(DA_CONFIG["output_dir"] / "用户行为分布饼状图.html")
    return funnel, pie
