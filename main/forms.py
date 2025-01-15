from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField

from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    data = TextAreaField("Write Something:", validators=[DataRequired(), Length(min=1)])
    submit = SubmitField("Post!")
