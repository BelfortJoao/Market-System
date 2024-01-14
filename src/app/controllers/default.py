from app import app, db
from app.models.forms import LoginForm, clientSearchForm, clientAtualizeForm, ProductSearchForm, ProductUpdateForm, clientCreateForm, carAddForm, carEditForm, PhoneAddForm, PhoneEditForm, CartForm
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.models.tables import User, Product, Car, Phone, Client, Kart, KartItem
from app import login_manager
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError


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
        user = User.query.filter_by(login = form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
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
        flash('Logout realizado com sucesso!')
        logout_user()
    return render_template('index.html')

#loads the sale first page sale_page1.html
#requires login
@app.route('/sale_page1', methods=['GET', 'POST'])
@login_required
def sale_page1():
    form = clientSearchForm()
    # retorna todos clientes do banco de dados
    clients = Client.query.all()
    results = []
    id = 0
    for client in clients:
        results.append(client.name)
        results.append(client.cpf)

    if form.validate_on_submit():
        name = form.clientName.data
        if name:
            client = Client.query.filter_by(name=name).first()
        if client:
            id = client.id
        else:
            flash('client not found')
        #open a new kart
        kart = Kart(
            client_id=id,
            total = 0
        )
        db.session.add(kart)
        db.session.commit()
        return redirect(url_for('sale_page2', id=id, kart=kart.id))
    return render_template('sale_page1.html', form=form, results=results)

# loads the sale second page sale_page2.html
# requires login
@app.route('/sale_page2/<int:id>-<kart>', methods=['GET', 'POST'])
@login_required
def sale_page2(id, kart):
    form = ProductSearchForm()
    # retorna todos produtos do banco de dados
    products = Product.query.all()
    results = []
    # para todo kartitem com o id do kart recupera itens
    kartitems = KartItem.query.filter_by(kart_id=kart).all()
    for product in products:
        results.append(product.name)
        results.append(product.code)
    if form.validate_on_submit():
        name = form.productName.data
        return redirect(url_for('sale_page3', name=name, id=id, kart=kart))
    return render_template('sale_page2.html', results=results, id=id, kart=kart, form=form, kartitems=kartitems)

#loads the sale third page sale_page3.html
#requires login
@app.route('/sale_page3/<name>-<int:id>-<int:kart>', methods=['GET', 'POST'])
@login_required
def sale_page3(name, id, kart):
    form = CartForm()  # Use o seu formulário CartForm

    # recupera o produto com o nome passado
    product = Product.query.filter_by(name=name).first()

    if form.validate_on_submit():
        quantidade = form.quantity.data

        # recupera o kart
        kart_instance = Kart.query.filter_by(id=kart).first()

        # seta o total do kart
        kart_instance.total = kart_instance.total + (quantidade * product.price)

        # cria um novo item no kart
        kartitem = KartItem(
            kart_id=kart_instance.id,
            product_id=product.id,
            quantity=quantidade,
            total=quantidade * product.price
        )

        db.session.add(kartitem)
        db.session.commit()

        flash('Produto adicionado ao carrinho com sucesso!', 'success')
        return redirect(url_for('sale_page2', id=id, kart=kart_instance.id))

    return render_template('sale_page3.html', product=product, form=form, id=id, kart=kart)

#sele confirm rote
@app.route('/sale_confirm/<int:id>-<int:kart>', methods=['GET', 'POST'])
@login_required
def sale_confirm(id, kart):
    # recupera o kart
    kart_instance = Kart.query.filter_by(id=kart).first()

    # seta o total do kart
    kart_instance.confirmed = True

    db.session.commit()

    flash('Compra confirmada com sucesso!', 'success')
    return redirect(url_for('sale_page1'))

#loads the search client page search_client.html
#requires login
@app.route('/search_client', methods=['GET', 'POST'])
@login_required
def search_client():
    form = clientSearchForm()
    # retorna todos clientes do banco de dados
    clients = Client.query.all()
    results = []
    for client in clients:
        results.append(client.name)
        results.append(client.cpf)

    if form.validate_on_submit():
        name = form.clientName.data
        return redirect(url_for('client', name=name))

    return render_template('search_client.html', results=results, form=form)

# Rota para exibir a página do cliente com base no parâmetro 'name'
@app.route('/client/<name>', methods=['GET', 'POST'])
@login_required
def client(name):
    form = clientAtualizeForm()
    car_form = carAddForm()
    phone_form = PhoneAddForm()
    client_cars = []

    client = Client.query.filter(or_(Client.name == name, Client.cpf == name)).first()

    if client:
        client_cars = Car.query.filter_by(client_id=client.id).all()
        client_phones = Phone.query.filter_by(client_id=client.id).all()

    if form.validate_on_submit() and form.submit.data:
        if form.clientName.data:
            client.name = form.clientName.data
        if form.clientAddress.data:
            client.address = form.clientAddress.data
        if form.clientCPF.data:
            client.cpf = form.clientCPF.data
        if form.clientEmail.data:
            client.email = form.clientEmail.data
        db.session.commit()
        flash('Cliente atualizado com sucesso!')
        return redirect(url_for('search_client'))

    #adiciona um novo telefone
    if phone_form.validate_on_submit() and phone_form.submit.data:
        try:
            phone = Phone(
                number=phone_form.number.data,
                client_id=client.id
            )
            db.session.add(phone)
            db.session.commit()
            flash('Telefone adicionado com sucesso!')
            return redirect(url_for('client', name=name))
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Erro ao adicionar telefone: {str(e)}", 'error')

    if car_form.validate_on_submit() and car_form.submit.data:
        try:
            carro = Car(
                name=car_form.modelo.data,
                client_id=client.id
            )
            db.session.add(carro)
            db.session.commit()
            flash('Carro adicionado com sucesso!')
            return redirect(url_for('client', name=name))
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Erro ao adicionar carro: {str(e)}", 'error')

    return render_template('client.html', cliente=client, form=form, carros=client_cars, car_form=car_form, phone_form=phone_form, phones=client_phones)

#add phone page
@app.route('/client/<name>/add_phone', methods=['POST'])
@login_required
def add_phone(name):
    phone_form = PhoneAddForm()

    client = Client.query.filter(or_(Client.name == name, Client.cpf == name)).first()

    if phone_form.validate_on_submit() and phone_form.submit.data:
        try:
            phone = Phone(
                number=phone_form.number.data,
                client_id=client.id
            )
            db.session.add(phone)
            db.session.commit()
            flash('Telefone adicionado com sucesso!')
            return redirect(url_for('client', name=name))
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Erro ao adicionar telefone: {str(e)}", 'error')

    return redirect(url_for('client', name=name))

#add car page
@app.route('/client/<name>/add_car', methods=['POST'])
@login_required
def add_car(name):
    car_form = carAddForm()

    client = Client.query.filter(or_(Client.name == name, Client.cpf == name)).first()

    if car_form.validate_on_submit() and car_form.submit.data:
        try:
            carro = Car(
                name=car_form.modelo.data,
                client_id=client.id
            )
            db.session.add(carro)
            db.session.commit()
            flash('Carro adicionado com sucesso!')
            return redirect(url_for('client', name=name))
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Erro ao adicionar carro: {str(e)}", 'error')

    return redirect(url_for('client', name=name))

@app.route('/new_client', methods=['GET', 'POST'])
@login_required
def new_client():
    form = clientCreateForm()

    if form.validate_on_submit():
        try:
            # Cria um novo cliente com os dados do formulário
            client = Client(
                name=form.clientName.data,
                address=form.clientAddress.data,
                cpf=form.clientCPF.data,
                email=form.clientEmail.data
            )

            # Adiciona o cliente ao banco de dados e comita as mudanças
            db.session.add(client)
            db.session.commit()

            # Redireciona para a página de pesquisa de clientes
            return redirect(url_for('search_client'))
        except IntegrityError:
            # Handle unique constraint violation (CPF already exists)
            db.session.rollback()
            flash("CPF already exists. Please use a different CPF.")
            return render_template('new_client.html', form=form)

    return render_template('new_client.html', form=form)
# new_product
@app.route('/new_product', methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductUpdateForm()

    if form.validate_on_submit():
        try:
            # Cria um novo produto com os dados do formulário
            product = Product(
                name=form.productName.data,
                price=form.productPrice.data,
                code=form.productCode.data,
                quantity=form.productQuantity.data
            )

            # Adiciona o produto ao banco de dados e comita as mudanças
            db.session.add(product)
            db.session.commit()

            # Redireciona para a página de pesquisa de produtos
            return redirect(url_for('search_product'))
        except IntegrityError:
            # Handle unique constraint violation (CPF already exists)
            db.session.rollback()
            flash("Code already exists. Please use a different code.")
            return render_template('new_product.html', form=form)

    return render_template('new_product.html', form=form)


@app.route('/search_product', methods=['GET', 'POST'])
@login_required
def search_product():
    form = ProductSearchForm()
    products = Product.query.all()
    results = []
    for product in products:
        results.append(product.name)
        results.append(product.code)

    if form.validate_on_submit():
        name = form.productName.data
        return redirect(url_for('product', name=name))

    return render_template('search_product.html',results=results, form=form)


@app.route('/product/<name>', methods=['GET', 'POST'])
@login_required
def product(name):
    product = Product.query.filter_by(name=name).first()
    if product is None:
        product = Product.query.filter_by(code=name).first()
    form = ProductUpdateForm(obj=product)  # Popula o formulário com os dados do produto

    if form.validate_on_submit():
        if form.productQuantity.data:
            product.quantity = form.productQuantity.data
        if form.productPrice.data:
            product.price = form.productPrice.data
        if form.productName.data:
            product.name = form.productName.data
        if form.productCode.data:
            product.code = form.productCode.data
        db.session.commit()
        return redirect(url_for('search_product'))

    return render_template('product.html', produto=product, form=form)

#delete client
@app.route('/delete_client/<name>', methods=['GET', 'POST'])
@login_required
def delete_client(name):
    client = Client.query.filter_by(name=name).first()
    if client is None:
        client = Client.query.filter_by(cpf=name).first()
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('search_client'))

#delete product
@app.route('/delete_product/<name>', methods=['GET', 'POST'])
@login_required
def delete_product(name):
    product = Product.query.filter_by(name=name).first()
    if product is None:
        product = Product.query.filter_by(code=name).first()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('search_product'))

@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    form = carEditForm()
    car_to_edit = Car.query.filter_by(id=car_id).first()
    id = car_to_edit.client_id
    #pega o nome do cliente baseado no id
    client = Client.query.filter_by(id=id).first()
    if form.validate_on_submit():
        if form.submit_edit.data:
            car_to_edit.name = form.modelo.data
            db.session.commit()
        elif form.submit_delete.data:
            db.session.delete(car_to_edit)
            db.session.commit()
        return redirect(url_for('client', name=client.name))
    return render_template('edit_car.html', form=form, car=car_to_edit)

#edit phone
@app.route('/edit_phone/<int:phone_id>', methods=['GET', 'POST'])
@login_required
def edit_phone(phone_id):
    form = PhoneEditForm()
    phone_to_edit = Phone.query.filter_by(id=phone_id).first()
    id = phone_to_edit.client_id
    #pega o nome do cliente baseado no id
    client = Client.query.filter_by(id=id).first()
    if form.validate_on_submit():
        if form.submit_edit.data:
            phone_to_edit.number = form.number.data
            db.session.commit()
        elif form.submit_delete.data:
            db.session.delete(phone_to_edit)
            db.session.commit()
        return redirect(url_for('client', name=client.name))
    return render_template('edit_phone.html', form=form, phone=phone_to_edit)

