from flask import Flask, render_template, request, redirect, url_for, flash
from db_models import User, Buyer, Owner, Dress, order_table
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from flask_login import LoginManager, current_user, login_user

app = Flask(__name__)
app.secret_key = 'annorah'

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

engine = create_engine("mysql+mysqldb://root:windowsql@localhost:3306/annorah_by_ama")
Session = sessionmaker(bind=engine)
session = Session()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)

def valid_login(email, password):
    """
    Check the email and password against 
    email and password fields in user model
    """
    user = session.query(User).filter(User.email == email).first()
    if user and check_password_hash(user.password_hash, password):
        return True
    else:
        return False

def allowed_file(filename):
    if '.' not in filename:
        return False
    file_extension = filename.rsplit('.', 1)[-1].lower()
    return file_extension in ALLOWED_EXTENSIONS


@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    """Login logic"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if valid_login(email, password):
            user = session.query(User).filter(User.email == email).first()
            login_user(user)
            if user.role == "buyer":
                flash('login successfull', 'success')
                return redirect (url_for('buyer_dashboard'))
            elif user.role == "Owner":
                flash('login successfull', 'success')
                return redirect (url_for('owner_page'))
        else:
            flash('Invalid username/password', 'error')
            #error = "Invalid username/password"
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'], strict_slashes=False)
def signup():
    """Signup Logic"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        password_hash = generate_password_hash(password)

        user = User(username=email, email=email, password_hash=password_hash, role="buyer")
        session.add(user)
        session.commit()
        buyer = Buyer(first_name=first_name, last_name=last_name, user_id=user.id)
        session.add(buyer)
        session.commit()
        flash('Signup Successfull', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/buyer-page', methods=['GET', 'POST'], strict_slashes=False)
def buyer_dashboard():
    dresses = session.query(Dress).all()
    user = current_user
    if user.role == 'buyer':
        buyer = user.buyer
        orders = session.query(order_table).filter(order_table.c.buyer_id == buyer.id).all()
        #print("orders: ", orders)
        dress_id_list = [order[1] for order in orders]
        print("list of ids that has been ordered by buyer:", dress_id_list)
        ordered_dresses = session.query(Dress).filter(Dress.id.in_(dress_id_list)).all()
        print("Dresses ordered:", ordered_dresses)
        return render_template('buyer_page.html', dresses=dresses, orders=ordered_dresses, name=buyer.first_name)
    else:
        flash('unauthorized', 'error')
        #return render_template('buyer_page.html', dresses=dresses, error_message='unauthorized')
    return render_template('buyer_page.html', dresses=dresses)

@app.route('/owner-page', methods=['GET', 'POST'], strict_slashes=False)
def owner_page():
    """Logic for owner page"""
    user = current_user
    if not user.is_authenticated:
        return redirect(url_for('login'))
    owner = session.query(Owner).first()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            #error_message = 'No file uploaded'
            #return render_template('owner_page.html', error_message=error_message)
        file = request.files['file']
        #if filename is empty
        if file.filename == '':
            flash('No file selected', 'error')
            #error_message = 'No file selected'
            #return render_template('owner_page.html', error_message=error_message)
        if file and allowed_file(file.filename):
            #securing filenames
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            name = request.form['name']
            price = request.form['price']    
            description = request.form['description']
            image_url = f'../static/images/{filename}'
            
            dress = Dress(
                name=name,
                price=price,
                description=description,
                image_url=image_url,
                owner_id=owner.id
            )
            session.add(dress)
            session.commit()
            flash('Item added successfully!', 'success')
            return render_template('owner_page.html', name=owner.first_name)
        else:
            flash('Invalid file type', 'error')
            #return render_template('owner_page.html', error_message='Invalid file type')
    return render_template('owner_page.html', name=owner.first_name)


@app.route('/', methods=['GET'], strict_slashes=False)
def landing_page():
    dresses = session.query(Dress).all()
    for dress in dresses:
        print(dress.image_url)
    return render_template('landing_page.html', dresses=dresses)


@app.route('/order-page/<int:dress_id>',methods=['GET', 'POST'])
def order_page(dress_id):
    dress = session.query(Dress).filter(Dress.id == dress_id).first()
    user = current_user
    if not dress:
        return render_template('order_page.html', error_message='Dress not found')
    if not user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == "POST":
        if user.role == 'buyer':
            buyer = user.buyer
            if buyer:
                session.execute(
                    order_table.insert().values(
                        buyer_id=buyer.id, dresses_id=dress_id
                    )
                )
                session.commit()
                flash('Order placed successfully', 'success')
                return redirect(url_for('buyer_dashboard'))
            else:
                return render_template('order_page.html', error_message='Buyer imformation not found')
        else:
            return render_template('order_page.html', error_message='unauthorized')
    
    return render_template('order_page.html', dress=dress, name=user.buyer.first_name)


if __name__ == "__main__":
    """ Main Function """
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000)