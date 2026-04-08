from utils.mysqlConnection import ConnectMysql

import pandas as pd


def csv_to_sql():
    """
    randomly select 1m data from csv file to MySql table
    """
    data = pd.read_csv('../data/UserBehavior.csv')
    data = data.sample(n=1000000, random_state=22)
    data['datetime'] = pd.to_datetime(data['timestamp'], unit='s')
    data['date'] = data['datetime'].dt.date
    data.info()
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


if __name__ == '__main__':
    # csv_to_sql()
    pass