from flask import Blueprint, render_template, url_for, redirect, request, current_app, abort
from app.models import Message, User
from app.forms import ProfileForm
from flask_login import current_user, login_required
from app.extensions import db, socketio
from app.utils import flash_errors, to_html
from flask_socketio import emit

app_bp = Blueprint('app', __name__)

online_user = []                # 用来装在线用户列表


# 主页
@app_bp.route('/')
def home():
    amount = current_app.config['CATCHAT_MESSAGE_PER_PAGE']     # 数据库里的时间应该是utc时间, 网页上的是本地 时间
    messages = Message.query.order_by(Message.timestamp.asc())[-amount:]  # 切片从最后面-15切到最后一位
    user_amount = User.query.count()
    return render_template('chat/home.html', messages=messages, user_amount=user_amount)


# 个人主页详细信息
@app_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.github = form.github.data
        current_user.website = form.website.data
        current_user.bio = form.bio.data
        db.session.commit()
        return redirect(url_for('app.home'))

    flash_errors(form) # 显示错误消息
    return render_template('chat/profile.html', form=form)


# 获取 用户弹窗信息
@app_bp.route('/get_profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('chat/_profile_card.html', user=user)


# 发送新消息
@socketio.on('new message')
def new_message(message_body):
    clean_html = to_html(message_body)
    message = Message(author=current_user._get_current_object(), body=clean_html)
    db.session.add(message)
    db.session.commit()
    emit('new message',
         {
             'message_html': render_template('chat/_message.html', message=message ),
             'message_body': clean_html,
             'gravatar': current_user.gravatar,
             'nickname': current_user.nickname,
             'user_id': current_user.id,
          }, broadcast=True)


# 更新在线人数
@socketio.on('connect')
def connect():
    global online_user              # 将列表变量申明为 全局变量
    if current_user.is_authenticated and current_user.id  not in online_user:
        online_user.append(current_user.id)
        emit('user_count',
             {'count': len(online_user)}, broadcast=True)


@socketio.on('disconnect')
def disconnect():
    global online_user
    if current_user.is_authenticated and current_user.id in online_user:
        online_user.remove(current_user.id)
        emit('user_count',
             {'count': len(online_user)}, broadcast=True)


# anonymous命令空间new message事件处理函数
@socketio.on('new message', namespace='/anonymous')   # 发现Url带有/anonymous， 会把消息显示 在anonymous框内
def new_anonymous_message(message_body):
    avatar = 'https://www.gravatar.com/avatar?d=mm'         # 赋于新的类型的头像
    nickname = 'Anonymous'                                  # 别名都为anonymous
    emit('new message',
         {'message_html': render_template('chat/_anonymous_message.html',
                                          message=message_body,
                                          avatar=avatar,
                                          nickname=nickname,
                                          )},
         broadcast=True, namespace='/anonymous')


# anonymous_message.html
@app_bp.route('/anonymous')
def anonymous():
    return render_template('chat/anonymous.html')


# 获取消息分布记录
@app_bp.route('/get_messages')
def get_messages():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['CATCHAT_MESSAGE_PER_PAGE']
    pagination = Message.query.order_by(Message.timestamp.desc()).paginate(page, per_page=per_page)
    messages = pagination.items

    return render_template('chat/_messages.html', messages=messages[::-1])


# 删除消息
@app_bp.route('/delete_message/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if current_user != message.author and not current_user.is_admin:
        abort(403)

    db.session.delete(message)
    db.session.commit()
    return '', 204