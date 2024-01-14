#log in form
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TelField, BooleanField, SubmitField, DecimalField, IntegerField, validators,  HiddenField
from wtforms.validators import DataRequired, Length, NumberRange

#login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Login')

class clientSearchForm(FlaskForm):
    clientName = StringField('Client Name', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Search')

class clientAtualizeForm(FlaskForm):
    clientName = StringField('Client Name')
    clientAddress = StringField('Client Address')
    clientCPF = StringField('Client CPF')
    clientEmail = StringField('Client Email')
    submit = SubmitField('Atualize')

class ProductSearchForm(FlaskForm):
    productName = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Search')

class ProductUpdateForm(FlaskForm):
    productName = StringField('Product Name')
    productPrice = DecimalField('Product Price', [validators.Optional()])
    productCode = StringField('Product Code')
    productQuantity = IntegerField('Product Quantity', [validators.Optional()])
    submit = SubmitField('Update')

class ProductCreateForm(FlaskForm):
    productName = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=20)])
    productPrice = DecimalField('Product Price', [validators.Optional()])
    productCode = StringField('Product Code', validators=[DataRequired(), Length(min=2, max=20)])
    productQuantity = IntegerField('Product Quantity', [validators.Optional()])
    submit = SubmitField('Create')

class clientCreateForm(FlaskForm):
    clientName = StringField('Client Name', validators=[DataRequired(), Length(min=2, max=20)])
    clientAddress = StringField('Client Address', validators=[DataRequired(), Length(min=2, max=20)])
    clientCPF = StringField('Client CPF', validators=[DataRequired(), Length(min=2, max=20)])
    clientEmail = StringField('Client Email', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Create')

class carEditForm(FlaskForm):
    id = HiddenField('ID do Carro')
    modelo = StringField('Modelo do Carro')
    submit_edit = SubmitField('Editar')
    submit_delete = SubmitField('Excluir')

class carAddForm(FlaskForm):
    modelo = StringField('Modelo do Carro')
    submit = SubmitField('Create')

class PhoneEditForm(FlaskForm):
    id = HiddenField('ID do Telefone')
    number = TelField('Número de Telefone')
    submit_edit = SubmitField('Editar')
    submit_delete = SubmitField('Excluir')

class PhoneAddForm(FlaskForm):
    number = TelField('Número de Telefone')
    submit = SubmitField('Criar')

# form de carrinho de compras
class CartForm(FlaskForm):
    id = HiddenField('ID do Produto')
    quantity = IntegerField('Quantidade', [validators.Optional(), NumberRange(min=1, max=100)])
    submit = SubmitField('Atualizar')
