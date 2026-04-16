import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar

from src.config import DA_CONFIG
from utils import ConnectMysql


def rfm_analysis():
    """
    数据中不含金额，所以只分析RF
    :return:
    """
    engine = ConnectMysql().get_engine()
    data = pd.read_sql("userbehavior", engine)
    rfm = (
        data[data["behavior"] == "buy"]
        .groupby(["user_id"])
        .agg({"datetime": "max", "date": "count"})
        .reset_index()
    )
    del data
    rfm.columns = ["user_id", "R", "F"]
    desc = rfm["R"].describe()
    r_bin = [desc["min"], desc["50%"], desc["75%"], desc["max"]]
    f_bin = [1, 2, 3, 4]
    labels = [1, 2, 3]
    labels_reverse = [3, 2, 1]
    rfm["R_score"] = pd.cut(
        rfm["R"], bins=r_bin, labels=labels_reverse, include_lowest=True
    )
    rfm["F_score"] = pd.cut(rfm["F"], bins=f_bin, labels=labels, include_lowest=True)
    rfm.info()
    rfm["RF"] = rfm["R_score"].astype(str) + rfm["F_score"].astype(str)
    print(rfm.head(5))
    rfm = rfm.groupby("RF").agg(cnt=("user_id", "count")).reset_index()
    rfm.info()
    print(rfm.head(5).to_string())
    bar = Bar()
    bar.add_xaxis(xaxis_data=rfm["RF"].tolist())
    bar.add_yaxis(series_name="", y_axis=rfm["cnt"].tolist())
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="RF分析柱状图"),
        xaxis_opts=opts.AxisOpts(type_="category", name="RF"),
        yaxis_opts=opts.AxisOpts(name="cnt"),
    )
    bar.set_series_opts(label_opts=opts.LabelOpts(position="top"))
    bar.render(DA_CONFIG["output_dir"] / "RF.html")
    return bar
