from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SubmitField,SelectField,TextAreaField
from wtforms.validators import DataRequired





class CreateForm(FlaskForm):
    name = StringField("name",validators=[DataRequired()])
    availability = StringField("availability eg-InStock", validators=[DataRequired()])
    condition = StringField("condition eg-new", validators=[DataRequired()])
    brand = StringField("brand eg-nike", validators=[DataRequired()])
    image = StringField("image eg-image_url", validators=[DataRequired()])
    price = IntegerField("price", validators=[DataRequired()])
    category = SelectField('Category', coerce=int)
    submit = SubmitField("submit")


class ReviewForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired()])
    text = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Submit')
