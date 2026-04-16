import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from src.config import DA_CONFIG
from utils import ConnectMysql

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


def basic_analysis():
    engine = ConnectMysql().get_engine()
    data = pd.read_sql("userbehavior", engine)
    data.info()
    pv_data = data[data["behavior"] == "pv"]
    buy_data = data[data["behavior"] == "buy"]
    del data
    date_pv = pv_data.groupby("date")["behavior"].count().reset_index(name="pv")
    date_buy = buy_data.groupby("date")["behavior"].count().reset_index(name="buy")
    hour_pv = pv_data.groupby("hour")["behavior"].count().reset_index(name="pv")
    del pv_data, buy_data
    buy_rate = pd.DataFrame()
    buy_rate["date"] = date_pv["date"]
    buy_rate["rate"] = date_buy["buy"] / date_pv["pv"]
    plt.figure(figsize=(12, 8), dpi=100)
    plt.subplot(2, 2, 1)
    sns.lineplot(data=date_pv, x="date", y="pv", label="PV")
    plt.xticks(rotation=15)
    plt.title("日PV")
    plt.subplot(2, 2, 2)
    sns.lineplot(data=date_buy, x="date", y="buy", label="Buy")
    plt.xticks(rotation=15)
    plt.title("日Buy")
    plt.subplot(2, 2, 3)
    sns.lineplot(data=hour_pv, x="hour", y="pv", label="PV")
    plt.title("时PV")
    plt.subplot(2, 2, 4)
    sns.barplot(data=buy_rate, x="date", y="rate", label="Buy Rate")
    plt.xticks(rotation=15)
    plt.title("购买转化率")
    plt.tight_layout()
    fig = plt.gcf()
    plt.savefig(DA_CONFIG["output_dir"] / "流量分析.jpg")
    plt.close()
    return fig
