from flask import Blueprint, render_template, url_for, redirect
from app.models import Message, User
from app.forms import ProfileForm
from flask_login import current_user, login_required
from app.extensions import db
from app.utils import flash_errors

app_bp = Blueprint('app', __name__)


@app_bp.route('/')
def home():
    messages = Message.query.order_by(Message.timestamp.asc())
    user_amount = User.query.count()
    return render_template('chat/home.html', messages=messages, user_amount=user_amount)


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


@app_bp.route('/get_profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('chat/_profile_card.html', user=user)


