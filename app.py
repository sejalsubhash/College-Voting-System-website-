'''
from flask import Flask, render_template, request, redirect, flash, send_from_directory,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import bcrypt
from PIL import Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html',user=user)
    
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')

class User_try(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    image_path = db.Column(db.String(255))
    
with app.app_context():
    db.create_all()

def is_valid_image(file_path):
    try:
        with Image.open(file_path) as img:
            return img.width == img.height == 100
    except Exception as e:
        print(f"Error: {e}")
        return False

app.config['UPLOAD_FOLDER'] = r'C:\Users\Sejal\Desktop\Folder1\candidate_images'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if not is_valid_image(file_path):
            os.remove(file_path)  # Remove the file if it's not valid
            return render_template('index.html', error_message='Invalid image dimensions. Please upload an image with 100x100 pixels.')
            return redirect(request.url)

        # Assuming you have a User model
        new_user = User_try(username='username', image_path=filename)
        db.session.add(new_user)
        db.session.commit()

        flash('File uploaded successfully')
        return redirect('/')
    
@app.route('/user_images')
def user_images():
    users = User_try.query.all()
    return render_template('user_images.html', users=users)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index_():
    # Fetch users from the database and pass them to the template
    users = User_try.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
'''
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Change this to your actual database URI
app.config['SECRET_KEY'] = 'secret_key'  # Change this to a random secret key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define the User class for Flask-Login
class voter_login(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Flask-Login user loader function
@login_manager.user_loader
def load_user(user_id):
    return voter_login.query.get(int(user_id))

# Registration form
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        # Handle form submission and save the data to the database
        # Example: Saving the data to the User model
        user = voter_login(
            name=request.form['fullName'],
            username=request.form['username'],
            email=request.form['email'],
            password=bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('signin'))

    # Pass user information to the registration form template
    return render_template('register.html', user=current_user)

# Sign-in route
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = voter_login.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            return redirect(url_for('user_home'))

        return render_template('signin.html', login_error=True)

    return render_template('signin.html', login_error=False)

# User home route
@app.route('/user_home')
@login_required
def user_home():
    return f"Welcome, {current_user.name}!"

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
