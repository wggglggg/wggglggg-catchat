from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app

import hashlib


# 用户
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)   # 不能为空
    nickname = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))
    github = db.Column(db.String(255))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(500))
    email_hash = db.Column(db.String(128))

    # 关联 Message 中的author
    messages = db.relationship('Message', back_populates='author', cascade='all')

    # 初始化, 生成邮箱散列值 hash
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_email_hash()

    def generate_email_hash(self):
        if self.email is not None and self.email_hash is None:
            # 使用hashlib库中的Md5算法, 将邮箱转成16进制
            print('self.email', self.email)
            self.email_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
            print('self.email_hash', self.email_hash)

    # 转换成 hash值 密码
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 校验登录密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成头像对应的URL
    @property
    def gravatar(self):
        return 'https://gravatar.com/avatar/%s?d=monsterid' % self.email_hash

    @property
    def is_admin(self):
        return self.email == current_app.config['CATCHAT_ADMIN_EMAIL']


class Guest(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False


# 消息
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 外键 关联 User 表中的messages
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='messages')
