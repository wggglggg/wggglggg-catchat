from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional,URL


# 用户的个人资料Form
class ProfileForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired(), Length(1, 64)])
    github = StringField('Github', validators=[Optional(), URL(), Length(0,128)])
    website = StringField('Website', validators=[Optional(), URL(), Length(0,128)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(0,400)])