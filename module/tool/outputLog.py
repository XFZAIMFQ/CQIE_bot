import logging
import sys


def outputLog():
    """输出日志"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # 创建一个 StreamHandler 以将日志输出到 stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # 设置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


log = outputLog()
# if __name__ == '__main__':
#     while True:
#         logger.debug('Debug message')
#         logger.info('Info message')
#         logger.warning('Warning message')
#         logger.error('Error message')
#         logger.critical('Critical message')
#         time.sleep(1)
