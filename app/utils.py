from flask import flash


# 弹出 错误消息
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            # getattr(表单form, 错误的字段)
            # error 错误的消息
            flash("Error in the %s field - %s" % (getattr(form, field).label.text, error))