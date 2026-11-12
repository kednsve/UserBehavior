import pandas as pd
from matplotlib import pyplot as plt

from src.config import DA_CONFIG
from utils import ConnectMysql

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


def hot_analysis():
    engine = ConnectMysql().get_engine()
    data = pd.read_sql("userbehavior", engine)
    hot_pv = (
        data[data["behavior"] == "pv"]
        .groupby("product_id")
        .size()
        .reset_index(name="pv")
        .sort_values("pv", ascending=False)
        .head(10)
    )
    hot_buy = (
        data[data["behavior"] == "buy"]
        .groupby("product_id")
        .size()
        .reset_index(name="buy")
        .sort_values("buy", ascending=False)
        .head(10)
    )
    hot_cate = (
        data[data["behavior"] == "buy"]
        .groupby("category_id")
        .size()
        .reset_index(name="buy")
        .sort_values("buy", ascending=False)
        .head(10)
    )
    plt.figure(figsize=(5, 12), dpi=100)
    plt.subplot(3, 1, 1)
    plt.bar(hot_pv["product_id"].astype(str), hot_pv["pv"])
    plt.xticks(rotation=25)
    plt.title("hot_pv")
    plt.subplot(3, 1, 2)
    plt.bar(hot_cate["category_id"].astype(str), hot_cate["buy"])
    plt.xticks(rotation=25)
    plt.title("hot_cate")
    plt.subplot(3, 1, 3)
    plt.bar(hot_buy["product_id"].astype(str), hot_buy["buy"])
    plt.xticks(rotation=25)
    plt.title("hot_buy")
    plt.suptitle("热门商品Top10")
    plt.tight_layout()
    fig = plt.gcf()
    plt.savefig(DA_CONFIG["output_dir"] / "热门商品TOP10.jpg")
    plt.close()
    return fig
