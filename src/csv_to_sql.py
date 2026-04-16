import pandas as pd

from utils import ConnectMysql


def csv_to_sql():
    """
    randomly select 1m data from csv file to MySql table
    """
    data = pd.read_csv("../data/UserBehavior.csv")
    data = data.sample(n=1000000, random_state=22)
    data = data.astype({"user_id": str, "product_id": str, "category_id": str})
    data["datetime"] = pd.to_datetime(data["timestamp"], unit="s")
    data["date"] = data["datetime"].dt.date
    data["date"] = pd.to_datetime(data["date"])
    data = data[(data["date"] >= "2017-11-25") & (data["date"] <= "2017-12-03")]
    data["month"] = data["datetime"].dt.month
    data["hour"] = data["datetime"].dt.hour
    data.info()
    print(data.head(5))
    engine = ConnectMysql()
    data.to_sql(
        "userbehavior",
        engine.get_engine(),
        index=False,
        if_exists="replace",
        method="multi",
        chunksize=10000,
    )
