from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import time
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling

# Temporary storage (Replace with a database)
users = {}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("You need to log in first.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html', time=int(time.time()), user=session.get('user', {}).get('name'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        blood_group = request.form.get('blood_group')
        location = request.form.get('location')
        password = request.form.get('password')

        if email in users:
            flash("Email already exists! Please log in.", "warning")
            return redirect(url_for('login'))

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Store user details (Replace with a database)
        users[email] = {
            'name': name,
            'email': email,
            'phone': phone,
            'blood_group': blood_group,
            'location': location,
            'password': hashed_password
        }

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users.get(email)  # Fetch user from temporary storage

        if user and check_password_hash(user['password'], password):
            session['user'] = {'name': user['name'], 'email': user['email']}
            session['logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password. Try again.", "danger")

    return render_template('login.html')

@app.route('/about')
@login_required  # Protecting about route
def about():
    return render_template('about.html')

@app.route('/logout')
@login_required  # Protecting logout route
def logout():
    session.clear()  # Clear session on logout
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
