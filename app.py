from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from models import db, User, Material  # ✅ Import the same `db` instance

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Initialize db with app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.')
            return redirect(url_for('register'))

        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    materials = Material.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', materials=materials)

@app.route('/materials', methods=['GET', 'POST'])
@login_required
def materials():
    if request.method == 'POST':
        name = request.form.get('name')
        weight = request.form.get('weight')

        if not name or not weight:
            flash('Please fill all fields.')
            return redirect(url_for('materials'))

        try:
            weight_float = float(weight)
            if weight_float <= 0 or weight_float > 1000:
                flash('Weight must be between 0 and 1000 kg.')
                return redirect(url_for('materials'))

            # Add new material
            new_material = Material(name=name, weight=weight_float, user_id=current_user.id)
            db.session.add(new_material)
            db.session.commit()
            flash('Material added successfully!')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Weight must be a valid number.')
            return redirect(url_for('materials'))

    return render_template('materials.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
