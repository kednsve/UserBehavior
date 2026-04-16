import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Funnel, Pie

from utils import ConnectMysql


def analysis_funnel_pie():
    engine = ConnectMysql().get_engine()
    data = pd.read_sql("userbehavior", engine)
    counts = data["behavior"].value_counts()
    del data
    pv_cnt = int(counts.get("pv", 0))
    buy_cnt = int(counts.get("buy", 0))
    cart_cnt = int(counts.get("cart", 0))
    fav_cnt = int(counts.get("fav", 0))
    labels = ["PV", "收藏", "加购", "购买"]
    cnts = [pv_cnt, fav_cnt, cart_cnt, buy_cnt]
    funnel = (
        Funnel()
        .add("转化漏斗", [list(z) for z in zip(labels, cnts)])
        .set_global_opts(title_opts=opts.TitleOpts(title="转化漏斗分析"))
    )
    funnel.render("../data/用户转化漏斗图.html")
    pie = (
        Pie()
        .add("用户行为分布", [list(z) for z in zip(labels, cnts)])
        .set_global_opts(title_opts=opts.TitleOpts(title="用户行为分布"))
    )
    pie.render("../data/用户行为分布饼状图.html")
