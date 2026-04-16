"""
1.用户流量分析：PV 用户活跃时段
2.转化漏斗分析：浏览->购买
3.商品分析：热门商品
4.RFM分析
"""
from src import *

# 数据集：淘宝用户购物行为数据集 ----阿里天池数据集 dataset/649
# user_id  product_id  category_id  behavior  timestamp
# 用户ID    商品ID       商品类目ID    用户行为    时间戳
# behavior: pv      buy     cart        fav
#           点击     购买     加入购物车    收藏


if __name__ == "__main__":
    # 从100M数据中抽取1M，处理后存入数据库中
    # csv_to_sql()
    # 处理后的数据
    # user_id product_id category_id behavior timestamp datetime date month hour
    # 用户ID   商品ID     商品类目ID     用户行为  时间戳      日期      日期  月   时
    basic_analysis()
    analysis_funnel_pie()
    hot_analysis()
    rfm_analysis()
