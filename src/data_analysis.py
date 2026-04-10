from utils.mysqlConnection import ConnectMysql

import pandas as pd

"""
1.用户流量分析：PV 用户活跃时段
2.转化漏斗分析：浏览->购买
3.商品分析：热门商品

"""


# 数据集：淘宝用户购物行为数据集 ----阿里天池数据集 dataset/649
# user_id  product_id  category_id  behavior  timestamp
# 用户ID    商品ID       商品类目ID    用户行为    时间戳
# behavior: pv      buy     cart        fav
#           点击     购买     加入购物车    收藏

# 从100M数据中抽取1M，处理后存入数据库中
def csv_to_sql():
    """
    randomly select 1m data from csv file to MySql table
    """
    data = pd.read_csv('../data/UserBehavior.csv')
    data = data.sample(n=1000000, random_state=22)
    # 添加列：datetime yyyy-MM-dd HH:mm:ss
    data['datetime'] = pd.to_datetime(data['timestamp'], unit='s')
    # 添加列：date     yyyy-MM-dd
    data['date'] = data['datetime'].dt.date
    # 添加列：month
    data['month'] = data['date'].dt.month
    # 添加列：hour
    data['hour'] = data['date'].dt.hour
    data.info()
    # 无缺失值
    print(data.head(5))
    engine = ConnectMysql()
    data.to_sql(
        'userbehavior',
        engine.get_engine(),
        index=False,
        if_exists='replace',
        method='multi',
        chunksize=10000
    )


# 处理后的数据
# user_id product_id category_id behavior timestamp datetime date month hour
# 用户ID   商品ID     商品类目ID     用户行为  时间戳

def user_activity():
    engine = ConnectMysql().get_engine()
    data = pd.read_sql('userbehavior', engine)
    data.info()
    # 筛选出浏览与购买数据
    pv_data = data[data['behavior'] == 'pv']
    buy_data = data[data['behavior'] == 'buy']
    # 绘图数据准备
    x_hours = [i for i in range(24)]
    x_months = [i for i in range(1, 13)]
    # TODO


if __name__ == '__main__':
    # csv_to_sql()
    user_activity()

    pass
