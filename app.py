from flask import Flask, render_template, request, redirect, url_for
from db_models import User, Buyer, Owner
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
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


if __name__ == "__main__":
    """ Main Function """
    app.run(host='0.0.0.0', port=5000)