import os, click

from flask import Flask
from app.extensions import db, moment, csrf, login_manager
from app.blueprints.app import app_bp
from app.blueprints.auth import auth_bp
from app.blueprints.admin import admin_bp
from app.blueprints.oauth import oauth_bp
from config import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLAKS_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app


# 注册各种工具
def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)


# 注册蓝本
def register_blueprints(app):
    app.register_blueprint(app_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(oauth_bp)


# 命令行生成数据
def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        if drop:
            click.confirm('Are you sure to delete db?', abort=True)
            db.drop_all()
            click.echo('Drop tables')

        db.create_all()
        click.echo('Initialized database.')