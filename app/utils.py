import markdown
from flask import flash
from bleach import clean, linkify


# 弹出 错误消息
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            # getattr(表单form, 错误的字段)
            # error 错误的消息
            flash("Error in the %s field - %s" % (getattr(form, field).label.text, error))


# markdown 过滤掉一些tags
def to_html(raw):
    allowed_tags = [                                                # 允许 消息出现的tags
        'a', 'abbr', 'b', 'br', 'blockquote', 'code',
        'del', 'div', 'img', 'p', 'em', 'pre', 'strong',
        'span', 'ul', 'li', 'ol',
    ]
    allowed_attributes = ['src', 'title', 'alt', 'href', 'class']   # 允许 消息中出现的属性
    html = markdown.markdown(raw, output_format='html',
                             extensions=['markdown.extensions.fenced_code',
                                         'markdown.extensions.codehilite']
                             )          # 外面 再包一个<html>
    clean_html = clean(html, tags=allowed_tags, attributes=allowed_attributes)    # 用clean将信息中不允许tags attrs干掉
    return linkify(clean_html)                                   # linkify可以将信息的网址用 <a> 包起来
