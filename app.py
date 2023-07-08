from flask import Flask, render_template, request, redirect, url_for, flash
import os
import glob
from flask_bootstrap import Bootstrap
# from docx2pdf import convert
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


host = ''
port =   # Default port for MySQL
user = ''
password = ''
database = ''

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'F:/file_upload_application/static/uploads'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx','jpg'}

app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/ABHI/AppData/Roaming/DBeaverData/workspace6/.metadata/sample-database-sqlite-1/Chinook.db'
app.config['SECRET_KEY'] = '1234'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)


login_manager = LoginManager(app)
login_manager.login_view = 'login'



# class User(db.Model, UserMixin):
#     # your model fields and definitions here

#     def __init__(self, username):
#         self.username = username
#         # additional initialization if needed
#         self.id = None

#     def is_active(self):
#     # Define the logic to determine if the user is active
#     # For example, you can return True if the user is active and False otherwise
#         return True

#     def get_id(self):
#         # Return the unique identifier for the user (e.g., user ID as a string)
#         return str(self.id)

USERS = {
    'admin': {
        'username': 'admin',
        'password': 'password',
    }
}

@login_manager.user_loader
def load_user(user_id):
    user = USERS.get(user_id)
    if user:
        return User(user['username'])
    return None






# # Define the File model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))

    # folder = db.relationship('Folder', backref=db.backref('files', lazy=True))
    def __repr__(self):
        return f"File('{self.filename}', '{self.upload_date}')"

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

@app.route('/index')
@login_required
def index():
    files = get_files()
    folders = Folder.query.all()
    return render_template('index.html', files=files)

# @login_manager.user_loader
# def load_user(user_id):
#     if user_id is None:
#         return None
#     return User.query.get(user_id)

from flask_login import login_user

from flask import redirect, url_for, render_template, request,flash
from flask_login import login_user, current_user

# Define a dictionary to store user information
from flask_login import login_user


# from forms import LoginForm 

# ...



from flask_login import login_user

from flask_login import UserMixin

from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username

# ...
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('You must be logged in to access this page.', 'error')
    return redirect(url_for('login'))



@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
            
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = USERS.get(username)

            if user and user['password'] == password:
                login_user(User(username))
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
    else:
        print(form.errors)  # Print the form validation errors
        return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))




import os

SUPPORTED_EXTENSIONS = ['txt', 'pdf', 'docx','jpg','jpeg']

def file_exists(filename):
    return os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in SUPPORTED_EXTENSIONS

from werkzeug.utils import secure_filename
import time


def generate_unique_filename(filename):
    timestamp = str(int(time.time()))
    base_filename, extension = os.path.splitext(filename)
    new_filename = f"{base_filename}_{timestamp}{extension}"
    return new_filename

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    try:
        if request.method == 'POST':
            files = request.files.getlist('files')  # Retrieve the list of uploaded files
            print(files)
            if not files:
                flash('No files selected', 'error')
                return redirect(request.url)

            db_connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            cursor = db_connection.cursor()
            for file in files:
                if file.filename == '':
                    flash('No selected file', 'error')
                    return redirect(request.url)

                query = "SELECT * FROM file WHERE filename = %s"
                cursor.execute(query, (file.filename,))
                existing_file = cursor.fetchone()
                print(existing_file)
                print(file.filename)
                # Check if the file already exists
                if file_exists(file.filename):
                    print(file.filename)
                    flash('File already exists. Please rename the file or choose a different file.', 'error')
                    return redirect(request.url)

                # Check if the file is allowed
                if not allowed_file(file.filename):
                    print(file.filename)
                    flash('Invalid file extension. Supported formats are: {}'.format(', '.join(SUPPORTED_EXTENSIONS)), 'error')
                    return redirect(request.url)

                # Generate a new filename
                filename = file.filename
                print(filename)
                # new_filename = generate_unique_filename(filename)

                # Save the file to the upload folder with the new filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                query = "INSERT INTO file_test(filename, upload_date) VALUES (%s, %s)"
                cursor.execute(query, (filename, datetime.now()))
                print('executed')
                db_connection.commit()
            cursor.close()
            db_connection.close()

            flash('Files uploaded successfully!', 'success')
            return redirect(url_for('index'))

        return render_template('upload.html')
    except Exception as e:
        print("An error occurred while uploading files:", e)
        flash('An error occurred while uploading files. Please try again.', 'error')
        return redirect(url_for('upload'))

    return render_template('upload.html')


import time
import random
import string

def create_unique_folder(folder_name):
    # Generate a unique folder name
    timestamp = str(int(time.time()))
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    unique_folder_name = f"{folder_name}_{timestamp}_{random_string}"

    # Create the directory
    path = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder_name)
    
    # Check if the directory already exists
    while os.path.exists(path):
        # Directory already exists, generate a new unique folder name
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        unique_folder_name = f"{folder_name}_{timestamp}_{random_string}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], unique_folder_name)

    os.makedirs(path)

    return unique_folder_name


import os
import zipfile
import shutil
import uuid


import os
import time

import os

@app.route('/upload_folder', methods=['GET', 'POST'])
@login_required
def upload_folder():
    if request.method == 'POST':
        folder = request.files['folder']

        if 'folder' not in request.files:
            flash('No folder part', 'error')
            return redirect(request.url)

        # Check if the folder is empty
        if not folder.filename:
            flash('No selected folder', 'error')
            return redirect(request.url)

        # Check if the folder already exists
        folder_name = secure_filename(folder.filename)
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        if os.path.exists(folder_path):
            flash('Folder already exists. Please choose a different folder or rename the existing folder.', 'error')
            return redirect(request.url)

        # Save the folder and its files to the upload folder
        folder.save(folder_path)

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)
                new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name, relative_path)
                os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                shutil.copy2(file_path, new_file_path)

        flash('Folder uploaded successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('upload_folder.html')



@app.route('/folder/<int:folder_id>')
def folder_details(folder_id):
    folder = Folder.query.get(folder_id)
    if folder:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder.name)
        files = os.listdir(folder_path)
        return render_template('folder.html', folder=folder, files=files)
    else:
        flash('Folder not found.', 'error')
        return redirect(url_for('index'))

# @app.route('/upload/folder', methods=['GET', 'POST'])
# def upload_folder():
#     if request.method == 'POST':
#         # Handle the folder upload logic
#         folder = request.files['folder']

#         if folder.filename.endswith('.zip'):
#             # Handle zip file upload
#             folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder.filename)

#             # Save the uploaded folder
#             folder.save(folder_path)

#             try:
#                 # Extract the folder contents
#                 with zipfile.ZipFile(folder_path, 'r') as zip_ref:
#                     zip_ref.extractall(app.config['UPLOAD_FOLDER'])

#                 # Remove the uploaded zip file
#                 os.remove(folder_path)

#                 flash('Folder uploaded and extracted successfully!', 'success')
#                 return redirect(url_for('index'))
#             except zipfile.BadZipFile:
#                 # Remove the uploaded zip file if it's not a valid zip file
#                 os.remove(folder_path)

#                 flash('Invalid zip file. Please upload a valid zip file.', 'error')
#                 return redirect(url_for('upload_folder'))
#         else:
#             # Handle normal folder upload
#             folder_name = folder.filename
#             destination_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)

#             # Generate a unique destination folder name if it already exists
#             if os.path.exists(destination_folder):
#                 folder_name = str(uuid.uuid4())
#                 destination_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)

#             # Create a directory for the uploaded folder
#             os.makedirs(destination_folder)

#             # Copy the contents of the uploaded folder to the destination folder
#             folder.save(os.path.join(destination_folder, folder_name))

#             flash('Folder uploaded successfully!', 'success')
#             return redirect(url_for('index'))

#     return render_template('upload_folder.html')

@app.route('/folder/<int:folder_id>')
def open_folder(folder_id):
    folder = Folder.query.get(folder_id)
    if folder:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder.name)
        files = os.listdir(folder_path)
        return render_template('folder.html', folder=folder, files=files)
    else:
        flash('Folder not found.', 'error')
        return redirect(url_for('index'))


from datetime import datetime

import json
from flask import request, jsonify

@app.route('/search', methods=['POST'])
@login_required
def search():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
        search_option = request.form.get('search_option')

        if search_option == 'name':
            # Search files by name
            query = request.form.get('query')
            print('Searching by name:', query)  # Add this line for debug
            files = File.query.filter(File.filename.ilike(f'%{query}%')).all()
            print(files)
        elif search_option == 'date':
            # Search files by date
            query_date = request.form.get('query_date')

            # Check if a date is selected
            if not query_date:
                return json.dumps({'error': 'Please select a date'})

            print('Searching by date:', query_date)  # Add this line for debug
            try:
                query_date = datetime.strptime(query_date, '%Y-%m-%d').date()
            except ValueError:
                return json.dumps({'error': 'Invalid date format. Please enter a date in the format YYYY-MM-DD.'})

            files = File.query.filter(File.upload_date == query_date).all()
        else:
            # Invalid search option
            return json.dumps({'error': 'Invalid search option'})

        # Prepare the JSON response
        response = {
            'files': [
                {'filename': file.filename, 'upload_date': file.upload_date.strftime('%Y-%m-%d %H:%M:%S')}
                for file in files
            ]
        }

        return json.dumps(response)

    return 'Invalid request'


@app.route('/view/<filename>')
@login_required
def view(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return render_template('view.html', filename=filename)
    else:
        flash('File not found', 'error')
        return redirect(url_for('index'))


@app.route('/download/<filename>', methods=['GET'])
@login_required
def download(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        print(file_path)
        print(filename)
        # return redirect(url_for('static', filename=app.config['UPLOAD_FOLDER'] + filename, _external=True))
        directory = app.config['UPLOAD_FOLDER']
        from flask import send_from_directory
        return send_from_directory(directory, filename, as_attachment=True)

    else:
        flash('File not found', 'error')
        return redirect(url_for('index'))


@app.route('/delete/<filename>')
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully', 'success')
    else:
        flash('File not found', 'error')
    return redirect(url_for('index'))


def get_files():
    files = []
    for file in glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*')):
        files.append(os.path.basename(file))
    return files


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')
