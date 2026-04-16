import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Funnel, Pie

from src.config import DA_CONFIG
from utils import ConnectMysql


def analysis_funnel_pie():
    engine = ConnectMysql().get_engine()
    data = pd.read_sql("userbehavior", engine)
    pv_cnt = data[data["behavior"] == "pv"]["user_id"].nunique()
    fav_cnt = data[data["behavior"] == "fav"]["user_id"].nunique()
    cart_cnt = data[data["behavior"] == "cart"]["user_id"].nunique()
    buy_cnt = data[data["behavior"] == "buy"]["user_id"].nunique()
    labels = ["PV", "收藏", "加购", "购买"]
    cnts = [pv_cnt, fav_cnt, cart_cnt, buy_cnt]
    funnel = (
        Funnel()
        .add("转化漏斗", [list(z) for z in zip(labels, cnts)])
        .set_global_opts(title_opts=opts.TitleOpts(title="转化漏斗分析"))
    )
    funnel.render(DA_CONFIG["output_dir"] / "用户转化漏斗图.html")
    pie = (
        Pie()
        .add("用户行为分布", [list(z) for z in zip(labels, cnts)])
        .set_global_opts(title_opts=opts.TitleOpts(title="用户行为分布"))
    )
    pie.render(DA_CONFIG["output_dir"] / "用户行为分布饼状图.html")
    return funnel, pie
