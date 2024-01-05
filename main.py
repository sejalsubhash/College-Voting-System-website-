from flask import Flask, render_template, request,flash, send_from_directory, redirect, url_for,session
from flask_login import LoginManager, login_user, login_required, current_user
from wtforms import StringField, SubmitField, validators
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_wtf import FlaskForm
import bcrypt
import random
import string
import os
from PIL import Image


app = Flask(__name__, template_folder='templates')
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = r'C:\Users\Sejal\Desktop\Folder1\candidate_images'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use 465 for SSL
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'sejalsubhash1104@gmail.com'
app.config['MAIL_PASSWORD'] = 'SEJ@LP@W@R'


db = SQLAlchemy(app)
app.secret_key = 'secret_key'
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])



# Database configuration
class voter_login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

with app.app_context():
    db.create_all()

class voter_registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    department = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    division = db.Column(db.String(5), nullable=False)
    student_id = db.Column(db.String(20), nullable=False, unique=True)
    
with app.app_context():
    db.create_all()
   
'''
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('voter_login.id'), nullable=False)
    fullName = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(100), nullable=False)
    division = db.Column(db.String(100), nullable=False)
    studentID = db.Column(db.String(100), unique=True, nullable=False)

    # Add other fields as needed

    user = db.relationship('voter_login', backref='registrations')

    def __init__(self, user_id, fullName, username, email, department, year, division, studentID):
        self.user_id = user_id
        self.fullName = fullName
        self.username = username
        self.email = email
        self.department = department
        self.year = year
        self.division = division
        self.studentID = studentID

with app.app_context():
    db.create_all()
'''

class candidate_registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.String(100),unique=True, nullable=False)
    candidateName = db.Column(db.String(100),  nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    className = db.Column(db.String(100), nullable=False)
    division = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    panelName = db.Column(db.String(100), unique=True, nullable=False)
   # user_image = db.Column(db.String(255),unique=True, nullable=False)
    file = db.Column(db.String(255),unique=True, nullable=False)
    
    def __init__(self, studentID, candidateName, gender, department,className, division, phone,email,panelName,file):
        self.studentID = studentID
        self.candidateName = candidateName
        self.gender = gender
        self.department = department
        self.className = className
        self.division = division
        self.phone = phone
        self.email = email
        self.panelName = panelName
       # self.user_image= user_image
        self.file= file

        
with app.app_context():
    db.create_all()
    
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(100), nullable=False)
    date_voted = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()
    
class AdminCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()
   
    
class info_validate(FlaskForm):
    phone = StringField('Contact Number', validators=[validators.Length(min=10, max=10, message="Contact number must have exactly 10 digits")])
    email = StringField('Email', validators=[validators.Email(message="Invalid email address")])
    submit = SubmitField('Submit')
     
     
# Functions to validate       
def generate_voter_id():
    characters = string.digits
    voter_id = ''.join(random.choice(characters) for _ in range(5))
    return int(voter_id)

def is_valid_image(file_path):
    try:
        with Image.open(file_path) as img:
            return img.width == img.height == 100
    except Exception as e:
        print(f"Error: {e}")
        return False
    

   
# Actual Workings of the Website
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the username already exists
        if voter_login.query.filter_by(username=username).first():
            return render_template('signup.html', username_exists=True)
        
        if voter_login.query.filter_by(email=email).first():
            return render_template('signup.html', email_exists=True)

        # Check if passwords match
        if password != confirm_password:
            return render_template('signup.html', password_mismatch=True)

        # Create a new user and add to the database
        new_user = voter_login(name=name, username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')

    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = voter_login.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['username'] = user.username
            return redirect('/user_home')

        return render_template('signin.html', login_error=True)

    return render_template('signin.html', login_error=False)


@app.route('/user_home')
def user_home():
    if session['username']:
        user= voter_login.query.filter_by(username=session['username']).first()
        return render_template('user_home.html',voter_login=voter_login,user=user)
    return redirect('/signin')

'''
@login_manager.user_loader
def load_user(user_id):
    return voter_login.query.get(int(user_id))

@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = voter_login.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['username'] = user.username
            return redirect('/user_home')

    return render_template('signin.html',)

@app.route('/registration', methods=['GET', 'POST'])

def registration():
    if 'username' in session:
        if request.method == 'POST':
            # Process the form data
            # For example, get form data
            fullName = request.form['fullName']
            department = request.form['department']
            year = request.form['year']
            division = request.form['division']
            studentID = request.form['studentID']

            # Create a new registration instance
            new_registration = Registration(
                id=session['user_id'],
                fullName=fullName,
                username=session['username'],  # assuming you want to associate the registration with the logged-in user
                email='',  # you can add email if you store it during registration
                department=department,
                year=year,
                division=division,
                studentID=studentID
            )

            # Add registration to the database
            db.session.add(new_registration)
            db.session.commit()

            return redirect('/success')  # Redirect to a success page

        return render_template('voter_registration.html')

    return redirect('/signin')
'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['fullName']
        username = request.form['username']
        email = request.form['email']
        department = request.form['department']
        year = request.form['year']
        division = request.form['division']
        student_id = request.form['studentID']
        
        if voter_registration.query.filter_by(student_id=student_id).first():
            return render_template('voter_registration.html', id_exists=True)
        
        if voter_registration.query.filter_by(username=username).first():
            return render_template('voter_registration.html', username_exists=True)
        
        if voter_registration.query.filter_by(email=email).first():
            return render_template('voter_registration.html', email_exists=True)


        new_voter = voter_registration(full_name=full_name, username=username, email=email,
                            department=department, year=year, division=division, student_id=student_id)

        db.session.add(new_voter)
        db.session.commit()

        return redirect('/user_images')
    
    return render_template('voter_registration.html')
    
    


@app.route('/admin_login',methods=['GET', 'POST'])
def admin_login():   
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the entered credentials match the predefined admin credentials
        admin = AdminCredentials.query.filter_by(username=username, password=password).first()

        if admin:
            # Redirect to the next page if the credentials match
            return redirect('/admin')
        else:
            error_message = 'Invalid username or password. Please try again.'

            return render_template('admin_login.html', error_message=error_message)

    return render_template('admin_login.html')


#for open Admin main Page
@app.route('/admin',methods=['GET', 'POST'])   
def admin():
    return render_template('admin.html')

#for open candidate_info  Page
@app.route('/canidate_reg',methods=['GET', 'POST'])
def canidate_reg():
    if request.method == 'POST':
        studentID = request.form['studentID']
        candidateName = request.form['candidateName']
        gender = request.form['gender']
        department = request.form['department']
        className = request.form['className']
        division = request.form['division']
        phone = request.form['phone']
        email = request.form['email']
        panelName = request.form['panelName']
        
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
            return render_template('candidate_info.html', error_message='Invalid image dimensions. Please upload an image with 100x100 pixels.')
            return redirect(request.url)

        new_user = candidate_registration(studentID = studentID, candidateName = candidateName, gender = gender, department = department,className=className, division = division, phone = phone,email = email,panelName = panelName, file=filename)
        db.session.add(new_user)
        db.session.commit()

        
        if candidate_registration.query.filter_by(studentID=studentID).first():
            return render_template('candidate_info.html', studentID_exists=True)
        
        if candidate_registration.query.filter_by(email=email).first():
            return render_template('candidate_info.html', email_exists=True)
        
        if candidate_registration.query.filter_by(phone=phone).first():
            return render_template('candidate_info.html', phone_exists=True)
        
        if candidate_registration.query.filter_by(file=file).first():
            return render_template('candidate_info.html', file_exists=True)
        
        if candidate_registration.query.filter_by(panelName=panelName).first():
            return render_template('candidate_info.html', panel_exists=True)
        
        
        new_user = candidate_registration(studentID = studentID, candidateName = candidateName, gender = gender, department = department,className=className, division = division, phone = phone,email = email,panelName = panelName, file=filename)
        db.session.add(new_user)
        db.session.commit()

        flash('File uploaded successfully')
        return redirect('/admin')
    return render_template('candidate_info.html')

@app.route('/user_images')
def user_images():
    users = candidate_registration.query.all()
    print(users)  # Print users to the console for debugging
    return render_template('voting.html', users=users)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    error_message = None

    if request.method == 'POST':
        email = request.form['email']
        user = voter_login.query.filter_by(email=email).first()

        if user:
            token = serializer.dumps(email, salt='forgot-password')
            reset_url = url_for('reset_password', token=token, _external=True)
            
            message = Message(
                'Reset Your Password',
                sender='sejalsubhash1104@gmail.com',  
                recipients=[email]
            )
            message.body = f'Click the following link to reset your password: {reset_url}'

            mail.send(message)
            return redirect(url_for('index'))

        error_message = 'Email not found. Please check and try again.'

    return render_template('forgot_password.html', error_message=error_message)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    error_message = None

    try:
        email = serializer.loads(token, salt='forgot-password', max_age=3600)  # Token is valid for 1 hour
    except:
        error_message = 'Invalid or expired token.'
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        # Update the user's password in the database
        user = voter_login.query.filter_by(email=email).first()
        user.password = new_password
        db.session.commit()

        return redirect(url_for('signin'))

    return render_template('reset_password.html', email=email, error_message=error_message)

@app.route('/vote', methods=['POST'])
def vote():
    selected_candidate = request.form.get('btnradio')
    current_date = request.form.get('currentDate')

    if selected_candidate and current_date:
        # Insert vote into the database
        vote = Vote(candidate_name=selected_candidate, date_voted=current_date)
        db.session.add(vote)
        db.session.commit()
        message= "Your vote was successful! Thanks for Voting"
        return message

    return redirect('/user_home')

@app.route('/vote_count', methods=['GET', 'POST'])
def vote_count():
    candidate_counts = db.session.query(Vote.candidate_name, db.func.count(Vote.candidate_name).label('count')).group_by(Vote.candidate_name).all()

    # Get the candidate with the maximum votes
    max_vote_candidate = db.session.query(Vote.candidate_name, db.func.count(Vote.candidate_name).label('count')).group_by(Vote.candidate_name).order_by(db.func.count(Vote.candidate_name).desc()).first()

    return render_template('resultdashboard.html', candidate_counts=candidate_counts, max_vote_candidate=max_vote_candidate)

if __name__ == '__main__':
    app.run(debug=True)





        