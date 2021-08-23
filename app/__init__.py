import os, click

from flask import Flask, render_template
from app.extensions import db, moment, csrf, login_manager, socketio, oauth
from app.blueprints.app import app_bp
from app.blueprints.auth import auth_bp
from app.blueprints.admin import admin_bp
from app.blueprints.oauth import oauth_bp
from config import config
from flask_wtf.csrf import CSRFError
from app.models import User, Message


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
    socketio.init_app(app)
    oauth.init_app(app)


# 注册蓝本
def register_blueprints(app):
    app.register_blueprint(app_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(oauth_bp)


# 错误网页处理器
def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', description=e.description, code=e.code), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', description=e.description, code=e.code), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', description=e.description, code=e.code), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('error.html', description=e.description, code=e.code), 400


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

    # 用户 消息随机生成器
    @app.cli.command()
    @click.option('--message', default=300, help='Quantity of messages, default is 300')
    def forge(message):
        """generate fake data."""
        import random
        from sqlalchemy.exc import IntegrityError # 数据库add数据报错

        from faker import Faker
        fake = Faker()

        click.echo('Initializing the database')
        db.drop_all()
        db.create_all()

        click.echo('Forging the  data...')
        click.echo('Generating users...')
        for i in range(50):
            user = User(
                nickname=fake.name(),
                email=fake.email(),
                github=fake.url(),
                website=fake.url(),
                bio=fake.sentence()
            )
            db.session.add(user)
            try:            # 数据存入错误捕捉
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

        click.echo('Generating messages...')
        for i in range(message):
            message = Message(   # 随机生成消息的作者ID
                author=User.query.get(random.randint(1, User.query.count())),
                body=fake.sentence(),
                timestamp=fake.date_time_between('-30d', '-2d'),
                # 时间为前30天 --- 前2天 时段
            )
            db.session.add(message)

        db.session.commit()
        click.echo('Done.')

