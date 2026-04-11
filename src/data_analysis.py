from utils.mysqlConnection import ConnectMysql

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyecharts import options as opts
from pyecharts.charts import Funnel

plt.rcParams['font.sans-serif'] = ['SimHei']
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
    data['date'] = pd.to_datetime(data['date'])
    data=data[(data['date']>= '2017-11-25') & (data['date'] <= '2017-12-03')]
    # 添加列：month
    data['month'] = data['datetime'].dt.month
    # 添加列：hour
    data['hour'] = data['datetime'].dt.hour
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

def basic_analysis():
    engine = ConnectMysql().get_engine()
    data = pd.read_sql('userbehavior', engine)
    data.info()
    # 筛选出浏览与购买数据
    pv_data = data[data['behavior'] == 'pv']
    buy_data = data[data['behavior'] == 'buy']
    del data
    date_pv = pv_data.groupby('date')['behavior'].count().reset_index(name='pv')
    date_buy = buy_data.groupby('date')['behavior'].count().reset_index(name='buy')
    hour_pv = pv_data.groupby('hour')['behavior'].count().reset_index(name='pv')
    del pv_data,buy_data
    # 购买转化率
    buy_rate = pd.DataFrame()
    buy_rate['date']=date_pv['date']
    buy_rate['rate']=date_buy['buy']/date_pv['pv']
    # 画图
    plt.subplot(2,2,1)
    sns.lineplot(data=date_pv,x='date',y='pv',label='PV')
    plt.xticks(rotation=45)
    plt.title('日PV')
    plt.subplot(2,2,2)
    sns.lineplot(data=date_buy,x='date',y='buy',label='Buy')
    plt.xticks(rotation=45)
    plt.title('日Buy')
    plt.subplot(2,2,3)
    sns.lineplot(data=hour_pv,x='hour',y='pv',label='PV')
    plt.xticks(rotation=45)
    plt.title('时PV')
    plt.subplot(2,2,4)
    sns.barplot(data=buy_rate,x='date',y='rate',label='Buy Rate')
    plt.xticks(rotation=45)
    plt.title('购买转化率')
    plt.tight_layout()
    plt.show()


def other_analysis():
    engine = ConnectMysql().get_engine()
    data = pd.read_sql('userbehavior', engine)

    counts = data['behavior'].value_counts()

    pv_cnt = int(counts.get('pv', 0))
    buy_cnt = int(counts.get('buy', 0))
    cart_cnt = int(counts.get('cart', 0))
    fav_cnt = int(counts.get('fav', 0))

    funnel = (
        Funnel()
        .add("转化漏斗",
             [list(z) for z in zip(['PV', '收藏', '加购', '购买'], [pv_cnt, fav_cnt, cart_cnt, buy_cnt])])
        .set_global_opts(title_opts=opts.TitleOpts(title="转化漏斗分析"))
    )
    funnel.render('conversion_funnel.html')


if __name__ == '__main__':
    # csv_to_sql()
    # basic_analysis()
    other_analysis()