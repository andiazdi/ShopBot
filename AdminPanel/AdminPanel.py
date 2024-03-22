from flask import Flask, render_template, redirect, request, abort
from werkzeug.utils import secure_filename
from forms.ProductsForm import ProductsForm
from forms.CategoryForm import CategoryForm
import os

# Import dbActions
import sys
sys.path.insert(0, '/home/almaz/ShopBot/db/')
import dbActions

db_path = '/home/almaz/ShopBot/db/ShopDB.db'

db = dbActions.DB(db_path, dbActions.Logger()) 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'VERY_SECRET_KEY_/(0_0)\_'
# app.config['UPLOAD_FOLDER'] = r'D:\\Languages\\Python\\ShopBot\\Bot\\images'
host = '0.0.0.0'
debug = True


@app.route('/')
def index():
    products = db.get_products()
    categories = db.get_categories()
    return render_template('index.html', title='Админ панель',
                           products=products, categories=categories)


@app.route('/product',  methods=['GET', 'POST'])
def add_product():
    form = ProductsForm()
    categories = [el['title'] for el in db.get_categories()]
    form.category.choices = categories

    if form.validate_on_submit():
        title = form.title.data.capitalize()
        price = form.price.data
        count = form.count.data
        category = form.category.data
        filetype = secure_filename(form.file.data.filename).split('.')[-1]
        filename = fr'/home/almaz/ShopBot/AdminPanel/static/images/products'\
                   + fr'/{db.get_last_id("products") + 1}.{filetype}'
        form.file.data.save(filename)

        db.add_product(title, price, count, category, f'{db.get_last_id("products") + 1}.{filetype}')
        return redirect('/')

    return render_template('products.html', title='Добавление товара',
                           form=form)


@app.route('/product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    form = ProductsForm()
    categories = [el['title'] for el in db.get_categories()]
    form.category.choices = categories
    if request.method == "GET":
        product = db.get_product(id)
        if product:
            form.title.data = product['title']
            form.price.data = product['price']
            form.count.data = product['count']
            form.category.data = product['category']
            form.file.src = product['file']
        else:
            abort(404)
    if form.validate_on_submit():
        product = db.get_product(id)
        if product:
            title = form.title.data.capitalize()
            price = form.price.data
            count = form.count.data
            category = form.category.data
            filetype = secure_filename(form.file.data.filename).split('.')[-1]
            os.remove(fr"/home/almaz/ShopBot/AdminPanel/static/images/products/{db.get_product(id)['file']}")
            filename = fr'static/images/products' + fr'/{id}.{filetype}'
            form.file.data.save(filename)
            db.update_product(id, title, price, count, category, f'{id}.{filetype}')
            return redirect('/')
        else:
            abort(404)
    return render_template('products.html',
                           title='Редактирование товара',
                           form=form)


@app.route('/product_delete/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    category = db.get_product(id)
    if category:
        os.remove(fr"/home/almaz/ShopBot/AdminPanel/static/images/products/{db.get_product(id)['file']}")
        db.delete_product(id)
        return redirect('/')
    else:
        abort(404)


@app.route('/product_add/<int:id>', methods=['GET', 'POST'])
def product_add(id):
    category = db.get_product(id)
    if category:
        db.product_count_add(id)
        return redirect('/')
    else:
        abort(404)


@app.route('/product_reduce/<int:id>', methods=['GET', 'POST'])
def product_reduce(id):
    category = db.get_product(id)
    if category:
        db.product_count_reduce(id)
        return redirect('/')
    else:
        abort(404)


@app.route('/category',  methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        title = form.title.data.capitalize()
        filetype = secure_filename(form.file.data.filename).split('.')[-1]
        filename = fr'/home/almaz/ShopBot/AdminPanel/static/images/categories'\
                   + fr'/{db.get_last_id("categories") + 1}.{filetype}'
        form.file.data.save(filename)
        db.add_category(title, f'{db.get_last_id("categories") + 1}.{filetype}')
        return redirect('/')

    return render_template('category.html', title='Добавление категории',
                           form=form)


@app.route('/category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    form = CategoryForm()
    if request.method == "GET":
        category = db.get_category_by_id(id)
        if category:
            form.title.data = category['title']
        else:
            abort(404)
    if form.validate_on_submit():
        category = db.get_category_by_id(id)
        if category:
            title = form.title.data.capitalize()
            filetype = secure_filename(form.file.data.filename).split('.')[-1]
            try:
                os.remove(fr"/home/almaz/AdminPanel/ShopBot/AdminPanel/static/images/categories/{db.get_category_by_id(id)['file']}")
            except Exception as e:
                print(e)
            filename = fr'/home/almaz/ShopBot/AdminPanel/static/images/categories' \
                       + fr'/{id}.{filetype}'
            form.file.data.save(filename)
            db.update_category(id, title, fr'{id}.{filetype}')
            return redirect('/')
        else:
            abort(404)
    return render_template('category.html',
                           title='Редактирование категории',
                           form=form)


@app.route('/category_delete/<int:id>', methods=['GET', 'POST'])
def delete_category(id):
    category = db.get_category_by_id(id)
    if category:
        os.remove(fr"/home/almaz/ShopBot/AdminPanel/static/images/categories/{db.get_category_by_id(id)['file']}")
        db.delete_category(id)
        return redirect('/')
    else:
        abort(404)


if __name__ == '__main__':
    app.run(host=host, debug=debug)
