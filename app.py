from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User Model with Role-Based Authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Change to Integer
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def get_id(self):
        return str(self.id)  # Return id as string for Flask-Login



# Create the database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)  # No need to convert to int


@app.route('/')
def home():
    return render_template('index.html', time=int(time.time()), user=current_user if current_user.is_authenticated else None)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        blood_group = request.form.get('blood_group')
        location = request.form.get('location')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if User.query.filter_by(email=email).first():
            flash("Email already exists! Please log in.", "warning")
            return redirect(url_for('login'))

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        new_user = User(  # No need to manually set the `id`
            name=name, 
            email=email, 
            phone=phone, 
            blood_group=blood_group,
            location=location, 
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))  

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('home'))  # Redirect to home page after login 
        else:
            flash("Invalid email or password. Try again.", "danger")

    return render_template('login.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Links to User table
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Auto timestamp

    user = db.relationship('User', backref='donations')  # Relationship to User



@app.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    if request.method == 'POST':
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')

        print(f"DEBUG: User ID: {current_user.id}")  # Check if user is detected
        print(f"DEBUG: Amount: {amount}, Payment Method: {payment_method}")

        if not amount or float(amount) <= 0:
            flash("Please enter a valid donation amount!", "danger")
            return redirect(url_for('donate'))

        new_donation = Donation(
            user_id=current_user.id,  # Make sure current_user is logged in
            amount=float(amount),
            payment_method=payment_method
        )

        db.session.add(new_donation)
        db.session.commit()

        flash(f"Thank you for your donation of ₹{amount} via {payment_method}!", "success")
        return redirect(url_for('home'))

    return render_template('donate.html', user=current_user)


class BloodDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'), nullable=False)  
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='blood_donations')


@app.route('/blood-donation', methods=['GET', 'POST'])
@login_required  # Only logged-in users can access
def blood_donation():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        blood_group = request.form.get('blood_group')
        location = request.form.get('location')
        contact = request.form.get('contact')

        if not (name and age and blood_group and location and contact):
            flash("All fields are required!", "danger")
            return redirect(url_for('blood_donation'))

        try:
            new_donor = BloodDonation(
                user_id=current_user.id,
                name=name,
                age=int(age),
                blood_group=blood_group.upper(),
                location=location,
                contact=contact
            )
            db.session.add(new_donor)
            db.session.commit()

            flash("Thank you for registering as a blood donor!", "success")
            return redirect(url_for('home'))  

        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            print("Error:", e)

    return render_template('blood_donation.html')    


@app.route('/blood-donors')
@login_required
def blood_donors():
    donors = BloodDonation.query.order_by(BloodDonation.date.desc()).all()
    return render_template('blood_donors.html', donors=donors)



@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash("Unauthorized Access!", "danger")
        return redirect(url_for('home'))
    return render_template('admin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
