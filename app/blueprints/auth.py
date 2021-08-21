from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_user, logout_user, login_required

from app.extensions import db
from app.models import User, Message


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('app.home')

    if request.method == 'POST':    # 从网页获取email password remember
        email = request.form['email']
        password = request.form['password']
        remember_me = request.form.get('remember', False)

        if remember_me:             # 如果用户钩选了remeber_me为 True
            remember_me = True

        user = User.query.filter_by(email=email).first()

        if user is not None and user.verify_password(password):
            login_user(user, remember_me)       # 如果在数据库中已存在用户, 就校验用户输入的密码, 正确就登录
            return redirect(url_for('app.home'))        # 跳转到首面Home

        flash('Either the email or password was incorrect')     # 显示 错误的信息

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('app.home'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('app.home'))

    if request.method == 'POST':
        email = request.form['email'].lower()           # 从网页接收到email, 先转成小写

        user = User.query.filter_by(email=email).first()        # 从数据库查看是否存在相同的email

        if user is not None:                                    # 如果email被 人注册过, 谅返回消息
            flash('The email is already registered , please type a new one.')
            return redirect(url_for('auth.register'))

        nickname = request.form['nickname']                       # 从网页端拿别名与密码
        password = request.form['password']

        user = User(nickname=nickname, email=email)                 # 生成user对象
        user.set_password(password)                                 # 将密码生成序列Hash值
        db.session.add(user)                                      # 将新用户准备写入数据库
        db.session.commit()                                       # 最后确认写入数据库
        login_user(user, remember=True)                             # 用户登录 到网页
        return redirect(url_for('app.home'))

    return render_template('auth/register.html')
