import pymysql
import sqlalchemy

#数据库引擎模块
class ConnectMysql:
    def __init__(self):
        self.host = 'localhost'
        self.port = '3306'
        self.user = 'root'
        self.password = '123456'
        self.database = 'data_analysis'
        self.charset = 'utf8'

    def get_engine(self):
        url = (
                'mysql+pymysql://' + self.user + ':' + self.password +
                '@' + self.host + ':' + self.port + '/' + self.database +
                '?charset=' + self.charset
        )
        engine = sqlalchemy.create_engine(url)
        return engine


if __name__ == '__main__':
    engine = ConnectMysql().get_engine()
    engine.connect()