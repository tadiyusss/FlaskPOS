from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, SelectField, FileField, FloatField
from wtforms.validators import Length, DataRequired, Email, EqualTo

class ProductForm(FlaskForm):
    
    product_name = StringField('Product Name', validators=[DataRequired(), Length(1, 24), ])
    product_category = SelectField('Product Category')
    product_stocks = IntegerField('Product Stocks', validators=[DataRequired()])
    product_price = FloatField('Product Price', validators=[DataRequired()])
    product_visibility = SelectField('Product Visibility', choices=[('1', 'Visible'), ('0', 'Hidden')])
    product_image = FileField('Product Image', validators=[DataRequired()])
    submit = SubmitField('Add Product')

class EditProductForm(FlaskForm):
    
    product_name = StringField('Product Name', validators=[DataRequired(), Length(1, 24)])
    product_category = SelectField('Product Category')
    product_stocks = IntegerField('Product Stocks', validators=[DataRequired()])
    product_price = FloatField('Product Price', validators=[DataRequired()])
    product_visibility = SelectField('Product Visibility', choices=[('1', 'Visible'), ('0', 'Hidden')])
    product_image = FileField('Product Image')
    submit = SubmitField('Add Product')


class CategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired(), Length(1, 24)])
    submit = SubmitField('Add Category')