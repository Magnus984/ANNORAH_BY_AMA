from flask import Flask, render_template, request, redirect, url_for
from db_models import User, Buyer, Owner, Dress
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'images/dresses'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

engine = create_engine("mysql+mysqldb://root:windowsql@localhost:3306/annorah_by_ama")
Session = sessionmaker(bind=engine)
session = Session()

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
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if valid_login(email, password):
            user = session.query(User).filter(User.email == email).first()
            if user.role == "buyer":
                return redirect (url_for('buyer_dashboard'))
            elif user.role is Owner:
                return redirect (url_for('owner_page'))
        else:
            error = "Invalid username/password"
    return render_template('login.html', error=error)


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
        
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/buyer-page', methods=['GET', 'POST'], strict_slashes=False)
def buyer_dashboard():
    return render_template('buyer_page.html')


@app.route('/owner-page', methods=['GET', 'POST'], strict_slashes=False)
def owner_page():
    """Logic for owner page"""
    if request.method == 'POST':
        if 'file' not in request.files:
            error_message = 'No file uploaded'
            return render_template('owner_page.html', error_message=error_message)
        file = request.files['file']
        #if filename is empty
        if file.filename == '':
            error_message = 'No file selected'
            return render_template('owner_page.html', error_message=error_message)
        if file and allowed_file(file.filename):
            #securing filenames
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            name = request.form['name']
            price = request.form['price']    
            description = request.form['description']
            image_url = f'/images/dresses/{filename}'
            owner = session.query(Owner).first()
            dress = Dress(
                name=name,
                price=price,
                description=description,
                image_url=image_url,
                owner_id=owner.id
            )
            session.add(dress)
            session.commit()
            return render_template('owner_page.html', success_message='Item added successfully!')
        else:
            return render_template('owner_page.html', error_message='Invalid file type')
    return render_template('owner_page.html')


if __name__ == "__main__":
    """ Main Function """
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000)