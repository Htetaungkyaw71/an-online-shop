from flask import Flask, redirect, request, render_template, flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SubmitField,SelectField
from wtforms.validators import DataRequired
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required,current_user
import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from form import CreateForm,ReviewForm
from flask_gravatar import Gravatar




now = datetime.datetime.now()
date = now.strftime("%d %B %Y")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////portfolio projects/an online shop/item.db'
app.config['SECRET_KEY'] = 'adadiadjadhydjqddq27e2jdhUDA'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('error'))
        elif current_user.id != 1:
            return redirect(url_for('error'))
        return f(*args, **kwargs)
    return decorated_function

def logincart_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("you need to login")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function




class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False,)


db.create_all()





class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    availability = db.Column(db.String(80), nullable=False)
    condition = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            nullable=False)
    category = db.relationship('Category',backref = db.backref('items', lazy=True))
    cartitem = db.relationship('CartItem', backref='Product')
    carts = db.relationship("CartItem", back_populates="products")
    review = db.relationship("Review", back_populates="item")

db.create_all()





class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False,unique=True)
    password = db.Column(db.String(100), nullable=False)
    carts = db.relationship("CartItem", back_populates="owner")
    checkout = db.relationship("Checkout", back_populates="owner")
    reviewer = db.relationship("Review", back_populates="author")

db.create_all()




class CartItem(db.Model):
    __tablename__ = 'cartitem'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner = db.relationship("User", back_populates="carts")
    product_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    products = db.relationship("Item", back_populates="carts")



db.create_all()



class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    author = db.relationship("User",back_populates="reviewer")
    item_id = db.Column(db.Integer,db.ForeignKey("items.id"))
    item = db.relationship("Item",back_populates="review")
    text = db.Column(db.String(250), nullable=False)

db.create_all()



class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(250), nullable=False)


db.create_all()

class Checkout(db.Model):
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner = db.relationship("User", back_populates="checkout")
    quantity = db.Column(db.String(250), nullable=False)
    product = db.Column(db.String(250), nullable=False)
    total = db.Column(db.Integer,  nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phnumber = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    township = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)

db.create_all()


ROWS_PER_PAGE = 6
@app.route("/",methods=["GET","POST"])
def home():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.all()
    items = Item.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('index.html',
                           items = items,
                            categories=categories,
                           logged_in=current_user.is_authenticated
                           )

@app.route("/search",methods=["GET","POST"])
def search():
    q = request.args.get('q')
    if q:
        items = Item.query.filter(Item.name.contains(q)|Item.brand.contains(q)|Item.condition.contains(q)|Item.availability.contains(q)|Item.price.contains(q))
    return render_template('search.html',
                           items = items,
                           categories=Category.query.all(),
                           )


@app.route('/category/<int:id>')
def category(id):
    items = Item.query.filter_by(category_id=id).all()
    if items == "":
        flash("no products")
    categories = Category.query.all()
    return render_template('category.html',items=items,
                           categories=categories,
                           logged_in=current_user.is_authenticated
                           )


@app.route("/create",methods=["GET","POST"])
@admin_required
def create():
    form = CreateForm()
    choice_list = [(i.id, i.name) for i in Category.query.all()]
    form.category.choices=choice_list
    if form.validate_on_submit():
        item = Item(
            name = form.name.data,
            availability=form.availability.data,
            condition=form.condition.data,
            brand=form.brand.data,
            image=form.image.data,
            price=form.price.data,
            category=Category.query.get(form.category.data),
            date=date,
        )
        db.session.add(item)
        db.session.commit()
        flash('You were successfully create an item')
        return redirect(url_for('create'))
    return render_template('create.html',
                           form = form,
                           logged_in=current_user.is_authenticated
                           )


@app.route("/addtocart/<int:id>",methods=["GET","POST"])
@logincart_required
def add_to_cart(id):
    if request.method == "POST":
        new_cart = CartItem(
            owner = current_user,
            product_id=id,
            quantity = int(request.form.get('quantity'))
        )
        db.session.add(new_cart)
        db.session.commit()
        return redirect(url_for('cart'))




@app.route("/cart")
@logincart_required
def cart():
    total = 0
    carts = CartItem.query.filter_by(owner=current_user)
    for cart in carts:
        p = cart.products.price * cart.quantity
        total += p
    return render_template('cart.html',carts=carts, logged_in=current_user.is_authenticated,total=total)


def listToString(s):
    # initialize an empty string
    str1 = " "

    # return string
    return (str1.join(str(e) for e in s))

@app.route("/checkout",methods=["GET","POST"])
@logincart_required
def checkout():
    total = 0
    product_name = []
    product_quantity = []
    carts = CartItem.query.filter_by(owner=current_user)
    for cart in carts:
        p = cart.products.price * cart.quantity
        total += p
        product_name.append(cart.products.name)
        product_quantity.append(cart.quantity)
    if request.method == "POST":
        new = Checkout(
            owner=current_user,
            total=total,
            product=listToString(product_name),
            quantity=listToString(product_quantity),
            name=request.form.get('name'),
            phnumber=request.form.get('ph'),
            region=request.form.get('region'),
            township=request.form.get('township'),
            address=request.form.get('address')
        )
        db.session.add(new)
        db.session.commit()
        return render_template('order.html')
    return render_template('checkout.html',
                           logged_in=current_user.is_authenticated,carts=carts,total=total
                           )


@app.route("/delivery")
@logincart_required
@admin_required
def delivery():
    checkout = Checkout.query.all()
    return render_template('delivery.html',checkouts=checkout,logged_in=current_user.is_authenticated)


@app.route("/deletedelivery/<int:id>")
@logincart_required
@admin_required
def deletedelivery(id):
    delete_delivery = Checkout.query.get(id)
    db.session.delete(delete_delivery)
    db.session.commit()
    return redirect(url_for('delivery'))




@app.route("/deletecart/<int:id>")
def deletecart(id):
    cart = CartItem.query.get(id)
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for('cart'))





@app.route('/detail/<int:id>',methods=["GET","POST"])
def detail(id):
    login = current_user.is_authenticated
    form = ReviewForm()
    item = Item.query.get(id)
    categories = Category.query.all()
    if form.validate_on_submit():
        if not login:
            flash("you need to first login")
            return redirect(url_for('login'))
        else:
            new = Review(
                name=form.name.data,
                email=form.email.data,
                author=current_user,
                item=item,
                text=form.text.data)
            db.session.add(new)
            db.session.commit()
            return redirect(url_for('detail',id=item.id))
    return render_template('product-details.html',
                           item=item,
                           date=date,
                           categories=categories,
                           logged_in=current_user.is_authenticated,form=form
                           )



@app.route("/login",methods=['GET',"POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user:
            if check_password_hash(user.password,request.form.get('password')):
                login_user(user)
                flash("you are successfully login")
                return redirect(url_for('home'))
            else:
                flash("password is incorrect")
                return redirect(url_for('login'))

        else:
            flash("email doesn't exist")
            return redirect(url_for('login'))
    return render_template('login.html',
                           logged_in=current_user.is_authenticated
                           )


@app.route("/register", methods=['GET', "POST"])
def register():
    if request.method=="POST":
        hash_password = generate_password_hash(request.form.get('password'), salt_length=8)
        new_user = User(
                name=request.form.get('name'),
                email=request.form.get('email'),
                password=hash_password,
            )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("you are successfully register")
        return redirect(url_for('home'))
    return render_template('login.html',
                           logged_in=current_user.is_authenticated
                           )


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/delete/<int:id>")
@admin_required
def delete(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/edit/<int:id>",methods=["GET","POST"])
@admin_required
def edit(id):
    is_edit = True
    item = Item.query.get(id)

    editform = CreateForm(
        name=item.name,
        availability=item.availability,
        condition=item.condition,
        brand=item.brand,
        image=item.image,
        category=item.category,
        price=item.price,
    )
    choice_list = [(i.id, i.name) for i in Category.query.all()]
    editform.category.choices = choice_list
    if editform.validate_on_submit():
        item.name = editform.name.data
        item.availability = editform.availability.data
        item.condition = editform.condition.data
        item.brand = editform.brand.data
        item.image = editform.image.data
        item.category = Category.query.get(editform.category.data)
        item.price = editform.price.data
        db.session.commit()
        flash("successfully updated")
        return redirect(url_for('detail',id=item.id))
    return render_template('create.html',
                           form=editform,
                           is_edit=is_edit,
                           logged_in=current_user.is_authenticated
                           )








@app.route("/contact",methods=["GET","POST"])
def contact():
    login = current_user.is_authenticated
    if request.method == "POST":
        if not login:
            flash("you need to login")
            return redirect(url_for('login'))
        else:
            new = Contact(
                name=request.form.get('name'),
                email = request.form.get('email'),
                subject = request.form.get('subject'),
                text = request.form.get('message')
            )
            db.session.add(new)
            db.session.commit()
            flash("Your message is successfully received.I will contact you as soon as possible")
            return redirect(url_for('contact'))
    return render_template('contact-us.html',
                           logged_in=current_user.is_authenticated
                           )

@admin_required
@app.route("/message")
def cmessage():
    messages = Contact.query.all()
    return render_template('cmessage.html',messages=messages,logged_in=current_user.is_authenticated)






@app.route('/error')
def error():
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)