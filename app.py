from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Create a user loader function
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Create a simple user authentication (for demonstration purposes)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'password':  # Change this to a more secure method in production
            user = User('admin')
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Invalid password. Please try again.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    return redirect(url_for('login'))  # Redirect to login page after logout

# Database initialization
def init_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  description TEXT,
                  price REAL,
                  images TEXT,
                  videos TEXT,
                  category TEXT,
                  rating REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.form.get('search', '')
    category_filter = request.form.get('category', '')
    sort_by = request.form.get('sort_by', '')

    # Подсчет количества товаров в корзине
    cart_count = sum(session.get('cart', {}).values()) if 'cart' in session else 0

    conn = sqlite3.connect('products.db')
    c = conn.cursor()

    query = "SELECT * FROM products"
    params = []

    if search_query:
        query += " WHERE name LIKE ?"
        params.append('%' + search_query + '%')

    if category_filter:
        if search_query:
            query += " AND category = ?"
        else:
            query += " WHERE category = ?"
        params.append(category_filter)

    if sort_by:
        if sort_by == 'price_asc':
            query += " ORDER BY price ASC"
        elif sort_by == 'price_desc':
            query += " ORDER BY price DESC"
        elif sort_by == 'rating':
            query += " ORDER BY rating DESC"

    c.execute(query, tuple(params))
    products = c.fetchall()
    conn.close()

    return render_template('index.html', products=products, search_query=search_query, category_filter=category_filter, sort_by=sort_by, cart_count=cart_count)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = c.fetchone()
    conn.close()

    if product is None:
        return "Product not found", 404

    return render_template('product_detail.html', product=product)

@app.route('/admin', methods=['GET', 'POST'])
@login_required  # Protect the admin route with login required
def admin():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        rating = request.form['rating']

        image_files = request.files.getlist('images')
        image_paths = []
        for image in image_files:
            if image.filename != '':
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                image_paths.append(filename)  # Save only the filename

        video_files = request.files.getlist('videos')
        video_paths = []
        for video in video_files:
            if video.filename != '':
                filename = secure_filename(video.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video.save(filepath)
                video_paths.append(filename)  # Save only the filename

        images_str = ','.join(image_paths)
        videos_str = ','.join(video_paths) if video_paths else ''  # Handle empty list

        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute("INSERT INTO products (name, description, price, images, videos, category, rating) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (name, description, price, images_str, videos_str, category, rating))
        conn.commit()
        conn.close()

        return redirect(url_for('admin'))

    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()

    return render_template('admin.html', products=products)

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required  # Protect the edit route with login required
def edit_product(product_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        rating = request.form['rating']

        image_files = request.files.getlist('images')
        image_paths = []

        for image in image_files:
            if image.filename != '':
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                image_paths.append(filename)  # Save only the filename

        video_files = request.files.getlist('videos')
        video_paths=[]

        for video in video_files:
            if video.filename != '':
                filename=secure_filename(video.filename)
                filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
                video.save(filepath)
                video_paths.append(filename)  # Save only the filename

        conn=sqlite3.connect('products.db')
        c=conn.cursor()

        if image_paths:
            images_str=','.join(image_paths)
            c.execute("UPDATE products SET images=? WHERE id=?", (images_str ,product_id))

        if video_paths:
            videos_str=','.join(video_paths)
            c.execute("UPDATE products SET videos=? WHERE id=?", (videos_str ,product_id))

        c.execute("UPDATE products SET name=?, description=?, price=?, category=?, rating=? WHERE id=?",
                  (name ,description ,price ,category ,rating ,product_id))

        conn.commit()
        conn.close()

        return redirect(url_for('admin'))

    # Get current product data for editing
    conn=sqlite3.connect('products.db')
    c=conn.cursor()
    c.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product=c.fetchone()
    conn.close()

    if product is None:
        return "Product not found", 404

    return render_template('edit_product.html', product=product)

@app.route('/delete/<int:product_id>')
@login_required  # Protect the delete route with login required
def delete_product(product_id):
    conn=sqlite3.connect('products.db')
    c=conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))

# Cart functionality
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    session['cart'] = cart
    return jsonify({'success': True})

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    data = request.get_json()
    quantity = data.get('quantity', 1)

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    cart[str(product_id)] = int(quantity)
    session['cart'] = cart
    return jsonify({'success': True})

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        if str(product_id) in cart:
            del cart[str(product_id)]
            session['cart'] = cart
    return jsonify({'success': True})

@app.route('/cart')
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total_price=0)

    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    cart_items = []
    total_price = 0

    for product_id, quantity in session['cart'].items():
        c.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = c.fetchone()
        if product:
            item = {
                'id': product[0],
                'name': product[1],
                'price': product[3],
                'quantity': quantity
            }
            cart_items.append(item)
            total_price += product[3] * quantity

    conn.close()
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

if __name__=='__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)