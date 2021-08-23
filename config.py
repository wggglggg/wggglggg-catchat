import os, sys

# 根据config.py来获取wggglggg-catchat项目的绝对路径,类似: c:\xxxxx\xxxx\wggglggg-catchat\
basedir = os.path.abspath(os.path.dirname(__file__))

# 检测平台是windows还是其它平台, 再来决定是用哪一个路径头
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


# 基本的配置config
class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'oiawe3fmlkmzxcv093waekfzsdf<?##')

    # 数据库保存在哪里, 文件名是什么
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'wggglggg-catchat.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CATCHAT_MESSAGE_PER_PAGE = 15


# 开发者配置
class DevelopmentConfig(BaseConfig):
    pass


# 生产模式
class ProductionConfig(BaseConfig):
    pass


# 测试模式
class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_DRI = 'sqlite:///'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}