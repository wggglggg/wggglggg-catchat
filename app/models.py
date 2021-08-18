from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# 用户
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)   # 不能为空
    nickname = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))
    github = db.Column(db.String(255))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(500))

    # 关联 Message 中的author
    messages = db.relationship('Message', back_populates='author', cascade='all')

    # 转换成 hash值 密码
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 校验登录密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


# 消息
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 外键 关联 User 表中的messages
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='messages')