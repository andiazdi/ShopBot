from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    title = StringField('Название категории', validators=[DataRequired()])
    file = FileField('Изображение', validators=[DataRequired()])
    submit = SubmitField('Применить')
