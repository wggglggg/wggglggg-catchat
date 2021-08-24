import random

from flask import Blueprint, abort, render_template, redirect, url_for, flash
from app.extensions import oauth, db
from flask_login import current_user, login_user
from app.models import User

import os

oauth_bp = Blueprint('oauth', __name__)


# 注册远程程序
github = oauth.remote_app(
    name='github',
    consumer_key=os.getenv('GITHUB_CLIENT_ID'),
    consumer_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    request_token_params={'scope': 'user'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
)

google = oauth.remote_app(
    name='google',
    consumer_key=os.getenv('GOOGLE_CLIENT_IDD'),
    consumer_secret=os.getenv('GOOGLE_CLIENT_SECRETD'),
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

twitter = oauth.remote_app(
    name='twitter',
    consumer_key=os.getenv('TWITTER_CLIENT_ID'),
    consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
    base_url='https://api.twitter.com/1.1',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
)


# 服务提供商
providers = {
    'github': github,
    'google': google,
    'twitter': twitter,
}

# 获取用户资料端点
profile_endpoints = {
    'github': 'user',
    'google': 'userinfo',
    'twitter': 'account/verify_credentials.json?include_email=true'
}


# 登录
@oauth_bp.route('/login/<provider_name>')
def oauth_login(provider_name):
    if provider_name not in providers.keys():
        abort(404)
    if current_user.is_authenticated:
        return redirect(url_for('app.home'))

    callback = url_for('.oauth_callback', provider_name=provider_name, _external=True)
    return providers[provider_name].authorize(callback=callback)


# 用于获取用户 详细资料, 由于每个提供商资料对应的key名称不一样, 比如github的bio是用户简介, twitter是description
def get_social_profile(provider, access_token):

    profile_endpoint = profile_endpoints[provider.name]
    response = provider.get(profile_endpoint, token=access_token)

    if provider.name == 'twitter':
        username = response.data.get('name')
        website = response.data.get('url')
        github = ''
        email = response.data.get('email')
        bio = response.data.get('description')
    elif provider.name == 'google':
        username = response.data.get('name')
        website = response.data.get('link')
        github = ''                                    # github 设为空
        email = response.data.get('email')
        bio = ''                                        # google 没有 bio简介
    else:
        username = response.data.get('name')
        website = response.data.get('blog')
        github = response.data.get('html_url')
        email = response.data.get('email')
        bio = response.data.get('bio')

    return username, website, github, email, bio


# 用获取到的详细资料, 来查验数据库中是否存在此email, 如果不存在就给此email注册, 使用github拿来的详细资料填充到catchat中
@oauth_bp.route('/callback/<provider_name>')
def oauth_callback(provider_name):
    if provider_name not in providers.keys():
        abort(404)

    provider = providers[provider_name]                 # 从字典里拿到服务商
    response = provider.authorized_response()           # 像服务提供商出起post请求, 拿到服务商的响应

    if response is not None:                            # 从响应中获取 access令牌
        access_token = response.get('access_token')
    else:
        access_token = None

    if access_token is None:                            # 如果分析出令牌是 None, 提示被 拒绝
        flash('Access denied, please try again')
        return redirect(url_for('auth.login'))
                                                        # 令牌是true , 就获取详细的用户数据
    username, website, github, email, bio = get_social_profile(provider, access_token)

    user = User.query.filter_by(email=email).first()
    if user is None:                                    # 用分析出的详细数据 email, 来查找catchat数据库中是否存在此用户
        # password = str(random.randint(1111, 9999))
        user = User(email=email, nickname=username, github=github, website=website, bio=bio)
        db.session.add(user)
        # user.set_password(password)
        db.session.commit()
        login_user(user, remember=True)                  # 不存在此用户, 就用此email注册用户, 再登录
        # flash('your password is: %s ' % password)
        return redirect(url_for('app.profile'))

    login_user(user, remember=True)                     # 存在此用户, 就直接登录
    return redirect(url_for('app.home'))
