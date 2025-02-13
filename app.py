from flask import Flask, render_template, request
import time

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', time=int(time.time()))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data (Process and store it in a database if needed)
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        blood_group = request.form.get('blood_group')
        location = request.form.get('location')

        # Print for debugging (replace with database storage later)
        print(f"New Donor: {name}, {email}, {phone}, {blood_group}, {location}")

    return render_template('signup.html', time=int(time.time()))  # Add timestamp

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
