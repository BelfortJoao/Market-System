from app import app, db
from app.models.tables import User
from app.models.forms import LoginForm
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.models.tables import User
from app import login_manager
from sqlalchemy import or_
from app.models.tables import Client

@login_manager.user_loader
def load_user(user_id):
    # Esta função deve retornar um objeto de usuário ou None
    return User.query.get(int(user_id))

#loads the entry page index.html
@app.route('/index')
def index():
    return render_template('index.html')

#loads the login page login.html
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #flash('Login requested for user {}, remember_me={}'.format(
        #    form.username.data, form.remember_me.data))
        user = User.query.filter_by(login = form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            flash('Login realizado com sucesso!')
            return redirect(url_for('home'))
        else:
            flash('Login inválido!')
    return render_template('login.html', title='Sign In', form=form)

#loads the home page home.html
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

#loads the logout page logout.html
@app.route('/logout')
@app.route('/')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return render_template('index.html')

#loads the sale first page sale_page1.html
#requires login
@app.route('/sale_page1')
@login_required
def sale_page1():
    return render_template('sale_page1.html')

#loads the search client page search_client.html
#requires login
@app.route('/search_client', methods=['GET', 'POST'])
@login_required
def search_client():
    # retorna todos clientes do banco de dados
    clients = Client.query.all()
    results = []
    for client in clients:
        results.append(client.name)
        results.append(client.cpf)

    if request.method == 'POST':
        # Se a solicitação for do tipo POST, significa que o formulário foi enviado
        search_query = request.form.get('searchQueryInput')
        # Agora você pode usar o valor de 'search_query' em seu modelo, como necessário
        # Aqui você pode redirecionar para a página do cliente com base na resposta do formulário
        return redirect(url_for('client', name=search_query))
    return render_template('search_client.html', results=results)


# Rota para exibir a página do cliente com base no parâmetro 'name'
@app.route('/client/<name>')
@login_required
def client(name):
    cliente = Client.query.filter_by(name=name).first()
    print(cliente)
    return render_template('client.html', cliente=cliente)

#loads the search product page search_product.html
#requires login
@app.route('/search_product')
@login_required
def search_product():
    return render_template('search_product.html')

#

