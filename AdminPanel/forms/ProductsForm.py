from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired


class ProductsForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    price = IntegerField("Стоимость", validators=[DataRequired()])
    count = IntegerField("Количество", validators=[DataRequired()])
    category = SelectField('Категории', validators=[DataRequired()])
    file = FileField('Изображение', validators=[DataRequired()])
    submit = SubmitField('Применить', validators=[DataRequired()])
