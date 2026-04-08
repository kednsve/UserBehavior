import logging
import os


class Logger:
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }

    # 构造方法
    def __init__(self, log_name: str, level='info', log_path='../log', fmt='%(asctime)s - %(levelname)s: %(message)s'):
        self.log_path = log_path
        self.log_name = log_name
        self.fmt = logging.Formatter(fmt)
        self.logger = logging.getLogger()
        self.logger.setLevel(self.levels[level])

    # 设置logger对象
    def get_logger(self):
        path = os.path.join(self.log_path, self.log_name + '.log')
        log_handler = logging.FileHandler(path, mode='a', encoding='utf-8')
        log_handler.setFormatter(self.fmt)
        self.logger.addHandler(log_handler)
        return self.logger
